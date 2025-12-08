#include <iostream>
#include <Windows.h>
#include <vector>
#include <conio.h>
#include <chrono>
#include <string>
#include "includes/CNSL_HANDLER.cpp"
/* #include <fcntl.h>
#include <io.h>
#include <stdio.h> */

#pragma comment(lib, "user32.lib")

using namespace std;

#define arrowup 72
#define arrowdown 80
#define arrowleft 75
#define arrowright 77

enum direction : int {STOP, UP, RIGHT, LEFT, DOWN};

class PNT{
    public:
        int x;
        int y;
        PNT(int X, int Y){
            x = X;
            y = Y;
        };
        void reset(){
            x = 0;
            y = 0;
        }
        bool overlap(PNT comp){
            if(comp.x == x && comp.y == y){
                return true;
            }
            return false;
        }
        COORD tocoord(){
            COORD op;
            op.X = x;
            op.Y = y;
            return op;
        }
        COORD tosnakecoord(){
            COORD op;
            op.X = x * 2 + 2;
            op.Y = y + 2;
            return op;
        }
};

PNT snakepos(0, 0), fruitpos(0, 0);
PNT dim(30, 30); // dimensions
vector<PNT> body, previousbody;
HANDLE cnslhandle = GetStdHandle(STD_OUTPUT_HANDLE);
long long points;
bool gameover = false;
bool addsegment;
direction pd = STOP; // player direction
CNSL_HANDLER cnsl;

void start();
void newfruit();
void displayscreen();
void move();
void setdims();

int main(){
    //_setmode(_fileno(stdout), _O_U16TEXT);
    //_setmode(_fileno(stdout), _O_WTEXT);
    auto strt = chrono::steady_clock::now();
    //setdims();
    start();
    SetConsoleOutputCP(CP_UTF8);
    auto end = chrono::steady_clock::now();
    srand(chrono::duration_cast<chrono::nanoseconds>(end - strt).count());
    while(true){
        start();
        while(!gameover){
            Sleep(100);
            move();
        }
        getchar();
        gameover = false;
    }
}

void setdims(){
    //cnsl.setfontsize(20);
    /*cnsl.setfontsize(23);
    system("cls");
    string swidth, sheight;
    cout << "width: ";
    int width = 0, height = 0;;
    while(width <= 0){
        getline(cin, swidth);
        width = stoi(swidth);
        if(width <= 0){
            system("cls");
            cout << "Pleas input a valid width: ";
        }
    }
    system("cls");
    cout << "width: " << width;
    cout << "\nheight: ";
    while(height <= 0){
        getline(cin, sheight);
        height = stoi(sheight);
        if(height <= 0){
            system("cls");
            cout << "width: " << width;
            cout << "Pleas input a valid height: ";
        }
    }
    if(width < 12){
        width = 12;
    }else if(width > 45){
        width = 45;
    }
    if(height < 12){
        height = 12;
    }else if(height > 45){
        height = 45;
    }
    dim.x = width;
    dim.y = height;
    int fntsz = 1344 / width;
    int delim = 500 + 50 * (width - 12)/8;
    if(delim / height < fntsz){
        fntsz = delim / height;
    }
    cnsl.setfontsize(fntsz);*/
}

void newfruit(){
    do{
        fruitpos.x = rand() % (dim.x - 1) + 1;
        fruitpos.y = rand() % (dim.y - 1) + 2;
    }while(fruitpos.overlap(snakepos));
}

void start(){
    system("cls");
    cnsl.setfontsize(20);
    points = 0;
    gameover = false;
    body.clear();
    previousbody.clear();
    pd = STOP;
    snakepos.x = dim.x / 2;
    snakepos.y = dim.y / 2;
    newfruit();
    body.push_back(snakepos);
    previousbody.push_back(snakepos);
    /*PNT segment = snakepos;
    segment.x--;
    previousbody.push_back(segment);
    segment.x--;
    previousbody.push_back(segment);*/
    string output;
    for(int y = 0; y < dim.y + 4; y++){
        for(int x = 0; x < dim.x + 4; x++){
            if(x == 0 || x == dim.x + 3 || y == 0 || y == dim.y + 3){
                output += char(178);
                output += char(178);
            }else{
                output += "  ";
            }
        }
        COORD pos;
        pos.X = 0;
        pos.Y = y + 1;
        SetConsoleCursorPosition(cnslhandle, pos);
        cout << output;
        output = "";
    }
    displayscreen();
}

void displayscreen(){
    if(pd == LEFT){ // makes it look smooth
        COORD firstcoord = previousbody[previousbody.size()].tosnakecoord();
        firstcoord.X += 1;
        SetConsoleCursorPosition(cnslhandle, firstcoord); // tail
        cout << " ";
        SetConsoleCursorPosition(cnslhandle, previousbody[previousbody.size()].tosnakecoord()); // tail
        cout << " ";
        firstcoord = snakepos.tosnakecoord();
        firstcoord.X += 1;
        SetConsoleCursorPosition(cnslhandle, firstcoord); // head
        cout << char(219);
        SetConsoleCursorPosition(cnslhandle, snakepos.tosnakecoord()); // head
        cout << char(219);
    }else{
        SetConsoleCursorPosition(cnslhandle, previousbody[previousbody.size()].tosnakecoord()); // tail
        cout << "  ";
        SetConsoleCursorPosition(cnslhandle, snakepos.tosnakecoord()); // head
        cout << char(219) << char(219);
    }
    for(int i = 0; i < body.size(); i++){
        if(body[i].overlap(snakepos) && i > 1){
            gameover = true;
        }
        /*if(!body[i].overlap(previousbody[i + 1])){
            SetConsoleCursorPosition(cnslhandle, body[i].tosnakecoord());
            cout << char(219) << char(219);
        }
        /*if(!body[i].overlap(previousbody[i])){
            SetConsoleCursorPosition(cnslhandle, previousbody[i].tosnakecoord()); // no more body there
            cout << "  ";
        }*/
    }
    if(addsegment){
        SetConsoleCursorPosition(cnslhandle, body[body.size() - 1].tosnakecoord());
        cout << "  ";
        addsegment = false;
    }
    if(fruitpos.overlap(snakepos)){
        points++;
        SetConsoleCursorPosition(cnslhandle, fruitpos.tosnakecoord()); // replace the body there
        cout << char(219) << char(219);
        newfruit();
        addsegment = true;
    }else{
        SetConsoleCursorPosition(cnslhandle, fruitpos.tosnakecoord());
        cout << char(176) << char(176);
    }
    COORD cursor;
    cursor.X = 0;
    cursor.Y = 0;
    SetConsoleCursorPosition(cnslhandle, cursor);
    cout << "Points: " << points;
    if(gameover){
        system("cls");
        cnsl.setfontsize(100);
        SetConsoleCursorPosition(cnslhandle, cursor);
        cout << "GAME OVER!\nYOU SCORED " << points;
        if(points == 1){
            cout << " point!";
        }else{
            cout << " points!";
        }
        cout << "\n\nPress any key to play again! Press Ctrl+C to exit";
        Sleep(1500);
    }

    // DEBUG :: 

    /*cursor.X = 0;
    cursor.Y = 25;
    SetConsoleCursorPosition(cnslhandle, cursor);
    cout << "x: " << snakepos.x << "   \ny: " << snakepos.y << "   ";*/

    // :: END DEBUG
}

void move(){
    // Register keypress event, but don't let it swap direction,
    // IE don't let the player change from moving up to moving down
    // because then the snake would run into itself
    if(GetAsyncKeyState(VK_UP) || GetAsyncKeyState('w')){
        pd = (pd == DOWN) ? pd : UP;
    }else if(GetAsyncKeyState(VK_RIGHT) || GetAsyncKeyState('d')){
        pd = (pd == LEFT) ? pd : RIGHT;
    }else if(GetAsyncKeyState(VK_DOWN) || GetAsyncKeyState('s')){
        pd = (pd == UP) ? pd : DOWN;
    }else if(GetAsyncKeyState(VK_LEFT) || GetAsyncKeyState('a')){
        pd = (pd == RIGHT) ? pd : LEFT;
    }
    if(pd == UP){
        snakepos.y--;
        if(snakepos.y <= 0){
            snakepos.y += dim.y;
        }
    }else if(pd == RIGHT){
        snakepos.x++;
        if(snakepos.x > dim.x){
            snakepos.x -= dim.x;
        }
    }else if(pd == DOWN){
        snakepos.y++;
        if(snakepos.y > dim.y){
            snakepos.y -= dim.y;
        }
    }else if(pd == LEFT){
        snakepos.x--;
        if(snakepos.x <= 0){
            snakepos.x += dim.x;
        }
    }
    if(pd != STOP){
        for(int i = 0; i < body.size(); i++){
            if(i > previousbody.size()){
                previousbody.push_back(body[i]);
            }else{
                previousbody[i] = body[i];
            }
        }
        if(!addsegment){
            body.pop_back();
        }
        if(body.size() == 0){
            SetConsoleCursorPosition(cnslhandle, body[0].tosnakecoord());
            cout << "  ";
        }
        body.insert(body.begin(), snakepos);
        displayscreen();
    }
}