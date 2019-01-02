
#include <Arduino.h>
#include <EEPROM.h>

constexpr unsigned long SERIAL_SPEED    = 115200;

constexpr int PIN_SERIAL_RX             = 0;
constexpr int PIN_SERIAL_TX             = 1;

constexpr int PIN_LED                   = 13;

constexpr int INPUT_BUFFER_LENGTH       = 32;

constexpr unsigned long LED_TOGGLE_INTERVAL = 500;


typedef struct {
    char data[INPUT_BUFFER_LENGTH];
    uint8_t length;
} inputBuffer_t;
    
inputBuffer_t inputBuffer;
int inputCh;

bool ledOn = false;
uint32_t lastLEDToggleTime = 0;


void setup() {
    Serial.begin(SERIAL_SPEED, SERIAL_8N1);

    pinMode(PIN_LED, OUTPUT);
    
    turnOffLED();
        
    sendMessage(F("Ready"));
}

void loop() {
    loopSerial();
    loopLED();
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

void resetInputBuffer() {
    inputBuffer.data[0] = '\0';
    inputBuffer.length = 0;
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


// =========== Other stuff

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
