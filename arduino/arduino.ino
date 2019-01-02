
#include <Arduino.h>
#include <EEPROM.h>

constexpr uint32_t  SERIAL_SPEED    = 115200;

constexpr int PIN_SERIAL_RX             = 0;
constexpr int PIN_SERIAL_TX             = 1;

constexpr int PIN_LED                   = 13;
constexpr int PIN_MAINTANK_TRIGGER      = 4;
constexpr int PIN_MAINTANK_READ         = 3;
constexpr int PIN_AUXTANK_READ          = A0;

constexpr uint8_t INPUT_BUFFER_LENGTH   = 32;
constexpr uint8_t RING_BUFFER_LENGTH    = 16;

constexpr uint32_t  LED_TOGGLE_INTERVAL = 500;
constexpr uint32_t  MAINTANK_INTERVAL   = 100;
constexpr uint32_t  AUXTANK_INTERVAL    = 1000;
constexpr uint32_t  SEND_INTERVAL       = 60000;

constexpr uint32_t  MAINTANK_REJECT     = 290;  // reject readings that are more than this many uS apart
constexpr uint32_t  MAINTANK_TIMEOUT    = 1000; // timeout in uS for waiting for rising signal

constexpr uint32_t  AUXTANK_REJECT      = 10;   // reject readings that are more than this many apart

constexpr uint8_t ST_IDLE       = 0;
constexpr uint8_t ST_WAIT_RISE  = 1;
constexpr uint8_t ST_WAIT_FALL  = 2;
constexpr uint8_t ST_READ       = 3;


typedef struct {
    char data[INPUT_BUFFER_LENGTH];
    uint8_t length;
} inputBuffer_t;
    
typedef struct {
    uint32_t data[RING_BUFFER_LENGTH];
    uint8_t ptr;
    bool looped;
    uint32_t average;
    bool calcedAverage;
    uint32_t last;
} ringBuffer_t;
    
inputBuffer_t inputBuffer;
int inputCh;

bool ledOn = false;
uint32_t lastLEDToggleTime = 0;

volatile uint8_t mainTankState = ST_IDLE;
uint32_t lastMainTankReadTime = 0;
volatile uint32_t mainTankPulseTime = 0;

uint32_t lastAuxTankReadTime = 0;

uint32_t lastSendTime = 0;

ringBuffer_t mainTankBuffer;
ringBuffer_t auxTankBuffer;


void setup() {
    Serial.begin(SERIAL_SPEED, SERIAL_8N1);

    pinMode(PIN_LED, OUTPUT);
    
    pinMode(PIN_MAINTANK_TRIGGER, OUTPUT);
    pinMode(PIN_MAINTANK_READ, INPUT);
    attachInterrupt(digitalPinToInterrupt(PIN_MAINTANK_READ), readMainTank, CHANGE);
    
    turnOffLED();

    sendMessage(F("Ready"));
}

void loop() {
    loopSerial();
    loopLED();
    loopMainTank();
    loopAuxTank();
    loopSend();
    
    // TODO: add sensors detecting state of boiler/hot water heater?
}

void loopSerial() {
    while (Serial.available()) {
        inputCh = Serial.read();
        if ((inputCh == '\r') || (inputCh == '\n')) {
            if (inputBuffer.length) {
                processCommand();
            }
            resetInputBuffer();
        } else if (inputCh == 8) {  // backspace
            if (inputBuffer.length) {
                inputBuffer.length--;
                inputBuffer.data[inputBuffer.length] = '\0';
            }
        } else if (inputCh == 27) { // escape
            if (inputBuffer.length) {
                resetInputBuffer();
                send(F("CANCELED\n"));
            }
        } else if ((inputCh >= 32) && (inputCh <= 126)) {
            if (inputBuffer.length >= (INPUT_BUFFER_LENGTH - 1)) {
                resetInputBuffer();
                sendError(F("overflow"));
                return;
            }
            inputBuffer.data[inputBuffer.length++] = inputCh;
            inputBuffer.data[inputBuffer.length] = '\0';
        }
    }
}

void loopLED() {
    if ((millis() - lastLEDToggleTime) >= LED_TOGGLE_INTERVAL) {
        lastLEDToggleTime = millis();
        toggleLED();
    }
}

void loopMainTank() {
    switch (mainTankState) {
        case ST_IDLE:
            if ((millis() - lastMainTankReadTime) >= MAINTANK_INTERVAL) {
                lastMainTankReadTime = millis();
                mainTankState = ST_WAIT_RISE;
                digitalWrite(PIN_MAINTANK_TRIGGER, HIGH);
                delayMicroseconds(10);
                digitalWrite(PIN_MAINTANK_TRIGGER, LOW);
            }
            break;
        case ST_WAIT_RISE:
        case ST_WAIT_FALL:
            if ((millis() - lastMainTankReadTime) >= MAINTANK_TIMEOUT) {
                lastMainTankReadTime = millis();
                mainTankState = ST_IDLE;
                sendMessage(F("main tank timeout"));
            }
            break;
        case ST_READ:
            lastMainTankReadTime = millis();
            send(F("#main tank: "));
            sendLUInt(mainTankPulseTime);
            sendChar('\n');
            if ((mainTankPulseTime - ringBufferLast(&mainTankBuffer, mainTankPulseTime)) > MAINTANK_REJECT) {
                sendMessage(F("main tank reject"));
            } else {
                ringBufferInsert(&mainTankBuffer, mainTankPulseTime);
            }
            mainTankState = ST_IDLE;
            break;
    }
}

void loopAuxTank() {
    if ((millis() - lastAuxTankReadTime) >= AUXTANK_INTERVAL) {
        lastAuxTankReadTime = millis();
        int val = analogRead(PIN_AUXTANK_READ);
        send(F("#aux tank: "));
        sendInt(val);
        sendChar('\n');
        if ((val - ringBufferLast(&auxTankBuffer, val)) > AUXTANK_REJECT) {
            sendMessage(F("aux tank reject"));
        } else {
            ringBufferInsert(&auxTankBuffer, val);
        }
    }
}

void loopSend() {
    if ((millis() - lastSendTime) >= SEND_INTERVAL) {
        lastSendTime = millis();
        
        send(F("*M"));
        sendLUInt(ringBufferAverage(&mainTankBuffer));
        sendChar('\n');
        
        send(F("*A"));
        sendLUInt(ringBufferAverage(&auxTankBuffer));
        sendChar('\n');
    }
}

void processCommand() {
    char* cmd = inputBuffer.data;
    int len = inputBuffer.length;
    
    switch (cmd[0]) {
        case 'E':
            if (! processChecksum(cmd, len)) break;
        case 'e':
            processEEPROMCommand(cmd + 1);
            break;
        case 'M':
            if (! processChecksum(cmd, len)) break;
        case 'm':
            processMainTankCommand(cmd + 1);
            break;
        case 'A':
            if (! processChecksum(cmd, len)) break;
        case 'a':
            processAuxTankCommand(cmd + 1);
            break;
        default:
            sendError(F("invalid command"));
            break;
    }
}

bool processChecksum(char* cmd, int len) {
    if ((len <= 3) || (cmd[len - 3] != '~')) {
        sendError("CHK");
        return false;
    }
    char* hex = cmd + len - 2;
    len -= 3;
    cmd[len] = '\0';
    uint8_t sentCS = readHex(&hex);
    uint8_t calcCS = 0;
    for (int i = 0; i < len; i++)
        calcCS ^= cmd[i];
    if (sentCS != calcCS) {
        sendError("CHK");
        return false;
    }
    return true;
}



// =========== EEPROM commands

void processEEPROMCommand(char* cmd) {
    switch (cmd[0]) {
        case 'C':
        case 'c':
            cmdEEPROMClear(cmd + 1);
            break;
        default:
            sendError(F("invalid EEPROM command"));
            break;
    }
}

void cmdEEPROMClear(char* str) {
    for (int i = 0 ; i < EEPROM.length() ; i++) {
        EEPROM.update(i, 0);
    }
    sendOK();
}

// =========== Main Tank commands

void processMainTankCommand(char* cmd) {
    switch (cmd[0]) {
        case '?':
            ringBufferStatus(&mainTankBuffer);
            break;
        default:
            sendError(F("invalid main tank command"));
            break;
    }
}

// =========== Aux Tank commands

void processAuxTankCommand(char* cmd) {
    switch (cmd[0]) {
        case '?':
            ringBufferStatus(&auxTankBuffer);
            break;
        default:
            sendError(F("invalid aux tank command"));
            break;
    }
}

// =========== Interrupt Service Routine

void readMainTank() {
    switch (mainTankState) {
        case ST_WAIT_RISE:
            mainTankPulseTime = micros();
            mainTankState = ST_WAIT_FALL;
            break;
        case ST_WAIT_FALL:
            mainTankPulseTime = micros() - mainTankPulseTime;
            mainTankState = ST_READ;
            break;
    }
}

// =========== Other stuff

void resetInputBuffer() {
    inputBuffer.data[0] = '\0';
    inputBuffer.length = 0;
}

uint32_t ringBufferLast(const ringBuffer_t* buffer, uint32_t def) {
    if (buffer->looped || buffer->ptr) {
        return buffer->last;
    } else {
        return def;
    }
}

uint32_t ringBufferAverage(ringBuffer_t* buffer) {
    if (buffer->calcedAverage) {
        return buffer->average;
    } else if (buffer->looped) {
        uint32_t avg;
        for (int i = 0; i < RING_BUFFER_LENGTH; i++)
            avg += buffer->data[i];
        avg = avg / RING_BUFFER_LENGTH;
        buffer->average = avg;
        buffer->calcedAverage = true;
    } else if (buffer->ptr) {
        uint32_t avg;
        for (int i = 0; i < buffer->ptr; i++)
            avg += buffer->data[i];
        avg = avg / buffer->ptr;
        buffer->average = avg;
        buffer->calcedAverage = true;
    } else {
        return 0;
    }
}

void ringBufferInsert(ringBuffer_t* buffer, uint32_t val) {
    buffer->last = val;
    buffer->calcedAverage = false;
    buffer->data[buffer->ptr] = val;
    buffer->ptr = (buffer->ptr + 1) % RING_BUFFER_LENGTH;
    if (buffer->ptr == 0)
        buffer->looped = true;
}

void ringBufferStatus(const ringBuffer_t* buffer) {
    for (int i = 0; i < RING_BUFFER_LENGTH; i++) {
        send(F("buf "));
        sendInt(i);
        send(F(": "));
        sendLUInt(buffer->data[i]);
        if (buffer->ptr == i)
            send(F(" <-"));
        sendChar('\n');
    }
    send(F("looped: "));
    sendInt(buffer->looped);
    sendChar('\n');
    
    send(F("average: "));
    sendLUInt(buffer->average);
    sendChar('\n');
    
    send(F("calcedAverage: "));
    sendInt(buffer->calcedAverage);
    sendChar('\n');
    
    send(F("last: "));
    sendLUInt(buffer->last);
    sendChar('\n');
}


int readInt(char** strPtr) {
    bool neg = false;
    int i = 0;
    char* str = *strPtr;
    if (*str == '-') {
        str++;
        neg = true;
    }
    while ((*str >= '0') && (*str <= '9')) {
        i = (i * 10) + (*str - '0');
        str++;
    }
    *strPtr = str;
    return neg ? -i : i;
}

unsigned readUInt(char** strPtr) {
    unsigned i = 0;
    char* str = *strPtr;
    while ((*str >= '0') && (*str <= '9')) {
        i = (i * 10) + (*str - '0');
        str++;
    }
    *strPtr = str;
    return i;
}

unsigned readHex(char** strPtr) {
    unsigned i = 0;
    char* str = *strPtr;
    while (1) {
        if ((*str >= '0') && (*str <= '9')) {
            i = (i << 4) + (*str - '0');
            str++;
        } else if ((*str >= 'a') && (*str <= 'f')) {
            i = (i << 4) + (*str - 'a') + 10;
            str++;
        } else if ((*str >= 'A') && (*str <= 'F')) {
            i = (i << 4) + (*str - 'A') + 10;
            str++;
        } else
            break;
    }
    *strPtr = str;
    return i;
}

bool readDelim(char** strPtr) {
    return readDelim(strPtr, ',');
}

bool readDelim(char** strPtr, char delim) {
    char* str = *strPtr;
    if (*str == delim) {
        str++;
        *strPtr = str;
        return true;
    } else {
        return false;
    }
}

void send(const char* str) {
    Serial.print(str);
}

void send(const __FlashStringHelper *str) {
    Serial.print(str);
}

void sendChar(char ch) {
    Serial.print(ch);
}

void sendInt(int i) {
    Serial.print(i);
}

void sendLUInt(long unsigned i) {
    Serial.print(i);
}

void sendOK() {
    send(F("OK\n"));
}

void sendError(const char* msg) {
    sendChar('!');
    send(msg);
    sendChar('\n');
}

void sendError(const __FlashStringHelper *msg) {
    sendChar('!');
    send(msg);
    sendChar('\n');
}

void sendMessage(const char* msg) {
    sendChar('#');
    send(msg);
    sendChar('\n');
}

void sendMessage(const __FlashStringHelper *msg) {
    sendChar('#');
    send(msg);
    sendChar('\n');
}

void turnOnLED() {
    digitalWrite(PIN_LED, HIGH);
    ledOn = true;
}

void turnOffLED() {
    digitalWrite(PIN_LED, LOW);
    ledOn = false;
}

void toggleLED() {
    if (ledOn) turnOffLED();
    else turnOnLED();
}
