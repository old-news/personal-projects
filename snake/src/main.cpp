#include <math.h>
#include <graphx.h>
#include <ti/getcsc.h>
#include <ti/screen.h>
#include <stdlib.h>
#include <sys/timers.h>
#include <sys/util.h>
#include <string.h>
#include <sys/rtc.h>

using namespace std;

template <typename T>
class specialVector{
    private:
        int* ptr;
        int size;
        int allocatedsize;
    public:

        specialVector(int Size){
            ptr = (int*)malloc(Size * sizeof(T));
            allocatedsize = Size;
            size = Size;
        }

        specialVector(int Size, int Allocatedsize){
            ptr = (int*)malloc(Allocatedsize * sizeof(T));
            allocatedsize = Allocatedsize;
            size = Size;
        }
        
        int getsize(){
            return size;
        }
        int getallocatedsize(){
            return allocatedsize;
        }

        void push_back(T value){
            ptr[size] = value;
            size++;
        }

        void pop_front(){
            size--;
            for(int i = 0; i < size; i++){
                ptr[i] = ptr[i + 1];
            }
        }

        void setsize(int newsize){
            size = newsize;
        }

        void fill(T value){
            for(int i = 0; i < size; i++){
                ptr[i] = value;
            }
        }
        //setter and getter
        int &operator[](int idx){
            return ptr[idx];
        }

};

const short __SIZE__ = 8;
const unsigned char BGcolor = 0, SnakeColor = 255, AppleColor = 224;
specialVector<unsigned char> snakesegmentsx(5, (320 / __SIZE__) * (240 / __SIZE__));
specialVector<unsigned char> snakesegmentsy(5, (320 / __SIZE__) * (240 / __SIZE__));
unsigned char direction[2] = {1, 0};
unsigned char x = 2, y = 15;
unsigned char key = 0;
unsigned char apple[2] = {30, 15};
short score = 0;
bool alive = true;

void initgame(){
    direction[0] = 1; direction[1] = 0;
    x = 2;
    y = int(120 / __SIZE__);
    apple[0] = int(240 / __SIZE__); apple[1] = int(120 / __SIZE__);
    score = 0;
    alive = true;

    snakesegmentsx.setsize(5);
    snakesegmentsy.setsize(5);
    snakesegmentsx.fill(0);
    snakesegmentsy.fill(31);
}


int main(void){
    srand(rtc_Time());
    snakesegmentsy.fill(127);
    gfx_Begin();
    gfx_SetDrawBuffer();
    gfx_SetTextFGColor(254 - BGcolor);
    gfx_SetTextBGColor(0);
    initgame();

    while(!key || key <= 4){
        gfx_FillScreen(BGcolor);

        if(key != 0){
            if(key == 1){
                (direction[1] == 0) ? (direction[0] = 0, direction[1] = 1) : 0;
            }else if(key == 2){
                (direction[0] == 0) ? (direction[0] = -1, direction[1] = 0) : 0;
            }else if(key == 3){
                (direction[0] == 0) ? (direction[0] = 1, direction[1] = 0) : 0;
            }else if(key == 4){
                (direction[1] == 0) ? (direction[0] = 0, direction[1] = -1) : 0;
            }
        }

        x += direction[0];
        y += direction[1];
        
        gfx_SetColor(SnakeColor);
        for(short i = 0; i < snakesegmentsx.getsize(); i++){
            gfx_FillRectangle(__SIZE__*snakesegmentsx[i], __SIZE__*snakesegmentsy[i], __SIZE__ - 1, __SIZE__ - 1);
            if(snakesegmentsx[i] == x && snakesegmentsy[i] == y){
                alive = false;
            }
        }
        if(x < 0 || x > (320 / __SIZE__) || y < 0 || y > (240 / __SIZE__)){
            alive = false;
        }

        if(x == apple[0] && y == apple[1]){
            score++;
            do {
                apple[0] = rand() % (320 / __SIZE__);
                apple[1] = rand() % (240 / __SIZE__);
            } while(apple[0] == 0 && apple[1] == 0);
            /*bool insnake = false;
            for(int i = 0; i < snakesegmentsx.getsize(); i++){
                if(apple[0] == snakesegmentsx[i] && apple[1] == snakesegmentsy[i]){
                    insnake = true;
                }
            }
            if(insnake){
                vector<int> grid;
                vector<uint8_t> positions;
                positions.reserve(snakesegmentsx.getsize());
                for(int i = 0; i < snakesegmentsx.getsize(); i++){
                    positions.push_back(31 * snakesegmentsx[i] + snakesegmentsy[i]);
                }
                positions.sort();
                grid.reserve(1200);
                for(int i = 0; i < 1200; i++){
                    if(i != positions[0]){
                        grid.push_back(i);
                    }else{
                        positions.pop_front();
                    }
                }
                short index = rand() % grid.getsize();
                apple[0] = int(grid[index] / 31);
                apple[1] = round(31 * (grid[index] - int(grid[index] / 31)));
            }*/
            snakesegmentsx.push_back(x);
            snakesegmentsy.push_back(y);
        }

        gfx_SetColor(AppleColor);
        gfx_FillRectangle(__SIZE__*apple[0], __SIZE__*apple[1], __SIZE__ - 1, __SIZE__ - 1);
        
        snakesegmentsx.pop_front();
        snakesegmentsy.pop_front();
        snakesegmentsx.push_back(x);
        snakesegmentsy.push_back(y);
        
        gfx_SetTextXY(2, 2);
        gfx_PrintInt(score, 1);

        gfx_SwapDraw();

        if(!alive){
            delay(2000);
            /*while(!key){
                key = os_GetCSC();
            }*/
            initgame();
        }

        key = os_GetCSC();
        delay(110 * log10(__SIZE__));
    }



    gfx_End();
    
    return 0;
}