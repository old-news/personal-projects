#include <Windows.h>
#include <iostream>
#include <WinUser.h>
#include <conio.h>

#pragma comment(lib, "user32.lib")

using namespace std;

void cnslpos(int x, int y) {
	HANDLE cnslhandle = GetStdHandle(STD_OUTPUT_HANDLE);
	COORD pos;
	pos.X = x;
	pos.Y = y;
	SetConsoleCursorPosition(cnslhandle, pos);
}

class BTN {
public:
	string text;
	int width;
	int height;
	int x;
	int y;

	BTN(string newtext) {
		text = newtext;
	}
	BTN(int newwidth, int newheight) {
		width = newwidth;
		height = newheight;
	}
	BTN(string newtext, int newwidth, int newheight) {
		width = newwidth;
		height = newheight;
		text = newtext;
	}
	BTN(string newtext, int newwidth, int newheight, int newxpos, int newypos) {
		width = newwidth;
		height = newheight;
		text = newtext;
		x = newxpos;
		y = newypos;
	}
};

class CNSL_HANDLER {
public:

	void setfontsize(int fontsize) {
		CONSOLE_FONT_INFOEX cnslfont;
		cnslfont.cbSize = sizeof(cnslfont);
		cnslfont.dwFontSize.Y = fontsize;
		SetCurrentConsoleFontEx(GetStdHandle(STD_OUTPUT_HANDLE), FALSE, &cnslfont);
	}
	void setfont(string font) {
		CONSOLE_FONT_INFOEX cnslfont;
		if (font == "Consolas") {
			wcscpy(cnslfont.FaceName, L"Consolas");
		}
		else if (font == "Courier New") {
			wcscpy(cnslfont.FaceName, L"Courier New");
		}
		else if (font == "Lucida Console") {
			wcscpy(cnslfont.FaceName, L"Lucida Console");
		}
		else if (font == "Lucida Sans Typewriter") {
			wcscpy(cnslfont.FaceName, L"Lucida Sans Typewriter");
		}
		else if (font == "MS Gothic") {
			wcscpy(cnslfont.FaceName, L"MS Gothic");
		}
		else if (font == "NSimSun") {
			wcscpy(cnslfont.FaceName, L"NSimSun");
		}
		else if (font == "SimSun-ExtB") {
			wcscpy(cnslfont.FaceName, L"SimSun-ExtB");
		}
		SetCurrentConsoleFontEx(GetStdHandle(STD_OUTPUT_HANDLE), FALSE, &cnslfont);
	}
	void setfontweight(int wgt) {
		CONSOLE_FONT_INFOEX cnslfont;
		if (wgt == 0) {
			cnslfont.FontWeight = FW_NORMAL;
		}
		else {
			cnslfont.FontWeight = wgt;
		}
		SetCurrentConsoleFontEx(GetStdHandle(STD_OUTPUT_HANDLE), FALSE, &cnslfont);
	}
	void setfontfmly(string fmly) {
		CONSOLE_FONT_INFOEX cnslfont;
		if (fmly == "\0") {
			cnslfont.FontFamily = FF_DONTCARE;
		}
		else {
			//cnslfont.FontFamily = fmly;
		}
		SetCurrentConsoleFontEx(GetStdHandle(STD_OUTPUT_HANDLE), FALSE, &cnslfont);
	}
	void setfontfmly() {
		CONSOLE_FONT_INFOEX cnslfont;
		cnslfont.FontFamily = FF_DONTCARE;
		SetCurrentConsoleFontEx(GetStdHandle(STD_OUTPUT_HANDLE), FALSE, &cnslfont);
	}

	void add(BTN toadd) {
		HWND console = GetConsoleWindow();
		POINT mouse;
		//ScreenToClient(console, &mouse);
		string opt;
		opt += char(219);
		for (int i = 0; i <= toadd.width - 3; i++) {
			opt += char(223);
		}
		opt += char(219);
		cnslpos(toadd.x, toadd.y);
		cout << opt;
		opt = char(219);
		for (int i = 0; i <= toadd.width - 3; i++) {
			opt += ' ';
		}
		opt += char(219);
		for (int i = 0; i <= toadd.height - 3; i++) {
			cnslpos(toadd.x, toadd.y + i + 1);
			cout << opt;
		}
		opt = char(219);
		for (int i = 0; i <= toadd.width - 3; i++) {
			if(toadd.height == 1){
				opt += char(219);
			}else{
				opt += char(220);
			}
		}
		opt += char(219);
		cnslpos(toadd.x, toadd.y + toadd.height - 1);
		cout << opt;
	}
};