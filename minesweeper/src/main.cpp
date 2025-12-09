#include <math.h>
#include <graphx.h>
#include <ti/getcsc.h>
//#include <ti/getkey.h>
#include <ti/screen.h>
//#include <stdlib.h>
#include <sys/timers.h>
#include <sys/util.h>
#include <string.h>
#include <sys/rtc.h>
#include <time.h>

/*
Color works as follows:
0brrrbbbgg
where 'r' is a red bit, 'b' is a blue bit, and 'g' is a green bit
and '0b' is the binary prefix
*/

// Go here for documentation: https://ce-programming.github.io/toolchain/libraries

const uint8_t BG_color = 0, wall_color = 255, mapx = 9, mapy = 9, square_size = 25, cursor_color = 0b0011111;
const uint8_t pixel_adjust_x = (320 - (square_size * mapx)) / 2, pixel_adjust_y = (240 - (square_size * mapy)) / 2;
const uint8_t bomb_color = 0b01001010, bomb_count = 10;
uint8_t cursor_x = int(mapx / 2), cursor_y = int(mapy / 2);
uint8_t key = 0;
unsigned short clicks = 0;
uint8_t map[mapx][mapy];

void decode_tile_id(uint8_t x, uint8_t y, uint8_t id){
    uint8_t* xptr = &x;
    uint8_t* yptr = &y;
    *xptr = id % mapx;
    *yptr = int(id / mapx);
}

uint8_t decode_tile_x(uint8_t id){
    return id % mapx;
}

uint8_t decode_tile_y(uint8_t id){
    return int(id / mapx);
}

uint8_t encode_tile_id(uint8_t x, uint8_t y){
    return x + y * mapx;
}

void dig_xy(uint8_t x, uint8_t y);

void make_map(){
    /*unsigned short bomb_map_id_list_len = mapx * mapy - 9;
    unsigned short bomb_map_id_list[bomb_map_id_list_len];
    unsigned short bad_ids_len = 9;
    unsigned short bad_ids[9] = {
        encode_tile_id(cursor_x, cursor_y),
        encode_tile_id(cursor_x, cursor_y + 1),
        encode_tile_id(cursor_x, cursor_y - 1),
        encode_tile_id(cursor_x + 1, cursor_y - 1),
        encode_tile_id(cursor_x + 1, cursor_y),
        encode_tile_id(cursor_x + 1, cursor_y + 1),
        encode_tile_id(cursor_x - 1, cursor_y - 1),
        encode_tile_id(cursor_x - 1, cursor_y),
        encode_tile_id(cursor_x - 1, cursor_y + 1)
    };
    unsigned short index = 0;*/
    unsigned short loops = 0;
    for(unsigned short i = 0; i < bomb_count; i++){
        if(loops > 16384){
            break;
        }
        loops++;
        uint8_t x = rand() % mapx, y = rand() % mapy;
        if(map[x][y] != 10 && !(abs(x - cursor_x) <= 1 && abs(y - cursor_y) <= 1)){
            map[x][y] = 10;
        }else{
            i--;
        }
    }
    /*for(unsigned short i = 0; i < bomb_map_id_list_len; i++){
        //bool is_bad = false;
        if(abs(decode_tile_x(i) - cursor_x) <= 1 && abs(decode_tile_y(i) - cursor_y) <= 1){
            continue;
        }else{
            bomb_map_id_list[index] = i;
            index++;
        }
        /*for(uint8_t z = 0; z < bad_ids_len; z++){
            if(bad_ids[z] == i){
                is_bad = true;
                //break;
            }
        }
    }
    for(uint8_t i = 0; i < 9; i++){
        uint8_t x = decode_tile_x(bad_ids[i]), y = decode_tile_y(bad_ids[i]);
        map[x][y] = 12;
        dig_xy(x, y);
        map[x][y] = 0;
    }
    for(uint8_t i = 0; i < bomb_count; i++){
        unsigned short index = rand() % (bomb_map_id_list_len - i);
        unsigned short id = bomb_map_id_list[index];
        bomb_map_id_list[index] = bomb_map_id_list[bomb_map_id_list_len - i];
        uint8_t x = decode_tile_x(id), y = decode_tile_y(id);
        map[x][y] = 10;
    }*/
    for(uint8_t x = 0; x < mapx; x++){
        for(uint8_t y = 0; y < mapy; y++){
            if(map[x][y] == 10){
                continue;
            }
            uint8_t num = 0;
            bool at_top = true, at_bottom = true;
            if(y > 0){
                at_bottom = false;
                num += map[x][y - 1] == 10 ? 1 : 0;
            }
            if(y < mapy - 1){
                at_top = false;
                num += map[x][y + 1] == 10 ? 1 : 0;
            }
            if(x > 0){
                num += map[x - 1][y] == 10 ? 1 : 0;
                if(!at_top){
                    num += map[x - 1][y + 1] == 10 ? 1 : 0;
                }
                if(!at_bottom){
                    num += map[x - 1][y - 1] == 10 ? 1 : 0;
                }
            }
            if(x < mapx - 1){
                num += map[x + 1][y] == 10 ? 1 : 0;
                if(!at_top){
                    num += map[x + 1][y + 1] == 10 ? 1 : 0;
                }
                if(!at_bottom){
                    num += map[x + 1][y - 1] == 10 ? 1 : 0;
                }
            }
            map[x][y] = num;
        }
    }
}

void draw_map(){
    gfx_SetColor(wall_color);
    for(uint8_t x = 0; x <= mapx; x++){
        gfx_FillRectangle(square_size * x + pixel_adjust_x, pixel_adjust_y, 2, square_size * mapy);
    }
    for(uint8_t y = 0; y <= mapy; y++){
        gfx_FillRectangle(pixel_adjust_x, square_size * y + pixel_adjust_y, square_size * mapx + 2, 2);
    }
    /*gfx_SwapDraw();
    gfx_FillScreen(BG_color);
    for(int x = 0; x <= mapx; x++){
        gfx_FillRectangle(square_size * x + pixel_adjust_x, pixel_adjust_y, 2, square_size * mapy);
    }
    for(int y = 0; y <= mapy; y++){
        gfx_FillRectangle(pixel_adjust_x, square_size * y + pixel_adjust_y, square_size * mapx + 2, 2);
    }*/
}

void draw_cursor(){
    gfx_SetColor(cursor_color);
    gfx_FillRectangle(pixel_adjust_x + square_size * cursor_x + 2, pixel_adjust_y + square_size * (cursor_y + 1) - 2, square_size - 2, 2);
}

void clear_cursor(){
    gfx_SetColor(BG_color);
    gfx_FillRectangle(pixel_adjust_x + square_size * cursor_x + 2, pixel_adjust_y + square_size * (cursor_y + 1) - 2, square_size - 2, 2);
}

void set_text_at_xy(uint8_t x, uint8_t y){
    gfx_SetTextXY(pixel_adjust_x + square_size * x - 2 + int(square_size / 2), pixel_adjust_y + square_size * y - 2 + int(square_size / 2));
}

void set_text_at_cursor(){
    set_text_at_xy(cursor_x, cursor_y);
}

void draw_flag(){
    gfx_SetTextFGColor(bomb_color);
    set_text_at_cursor();
    gfx_PrintChar('F');
}

void draw_num_at_cursor(){
    gfx_SetTextFGColor(0b00011100);
    set_text_at_cursor();
    gfx_PrintChar('Y');
}

void draw_num_at_xy(uint8_t x, uint8_t y){
    uint8_t num = map[x][y];
    //gfx_SetTextFGColor(0b1111100);
    // PICKUP HERE
    // DO COLORS
    if(num == 0){
        gfx_SetTextFGColor(cursor_color);
    }else if(num == 1){
        gfx_SetTextFGColor(0b00010100);
    }else if(num == 2){
        gfx_SetTextFGColor(0b00000011);
    }else if(num == 3){
        gfx_SetTextFGColor(0b11100001);
    }else if(num == 4){
        gfx_SetTextFGColor(0b00011000);
    }else if(num == 5){
        gfx_SetTextFGColor(0b01100000);
    }else if(num == 6){
        gfx_SetTextFGColor(0b00011111);
    }else if(num == 7){
        gfx_SetTextFGColor(0b11111111);
    }else if(num == 8){
        gfx_SetTextFGColor(0b01001010);
    }
    set_text_at_xy(x, y);
    gfx_PrintInt(num, 1);
}

uint8_t get_surrounding_nums(uint8_t x, uint8_t y, uint8_t* numbers){
    uint8_t i = 0;
    bool at_top = true, at_bottom = true;
    if(y > 0){
        at_bottom = false;
        if(map[x][y - 1] < 10){
            numbers[i] = encode_tile_id(x, y - 1);
            i++;
        }
    }
    if(y < mapy - 1){
        at_top = false;
        if(map[x][y + 1] < 10){
            numbers[i] = encode_tile_id(x, y + 1);
            i++;
        }
    }
    if(x > 0){
        if(map[x - 1][y] < 10){
            numbers[i] = encode_tile_id(x - 1, y);
            i++;
        }
        if(!at_top && map[x - 1][y + 1] < 10){
            numbers[i] = encode_tile_id(x - 1, y + 1);
            i++;
        }
        if(!at_bottom && map[x - 1][y - 1] < 10){
            numbers[i] = encode_tile_id(x - 1, y - 1);
            i++;
        }
    }
    if(x < mapx - 1){
        if(map[x + 1][y] < 10){
            numbers[i] = encode_tile_id(x + 1, y);
            i++;
        }
        if(!at_top && map[x + 1][y + 1] < 10){
            numbers[i] = encode_tile_id(x + 1, y + 1);
            i++;
        }
        if(!at_bottom && map[x + 1][y - 1] < 10){
            numbers[i] = encode_tile_id(x + 1, y - 1);
            i++;
        }
    }
    return i;
}

void dig_xy(uint8_t x, uint8_t y){
    if(map[x][y] >= 100){
        return;
    }
    draw_num_at_xy(x, y);
    clicks += 1;
    if(map[x][y] != 0){
        map[x][y] += 100;
        return;
    }
    uint8_t nums[8];
    uint8_t length = get_surrounding_nums(x, y, nums);
    map[x][y] += 100;
    for(uint8_t i = 0; i < length; i++){
        uint8_t newx = decode_tile_x(nums[i]);
        uint8_t newy = decode_tile_y(nums[i]);
        if(map[newx][newy] >= 10){
            continue;
        }
        dig_xy(newx, newy);
    }
}

void clear_map(){
    for(int x = 0; x < mapx; x++){
        for(int y = 0; y < mapy; y++){
            map[x][y] = 0;
        }
    }
}

void init_round(){
    clicks = 0;
    os_GetCSC();
    key = 0;
    cursor_x = int(mapx / 2);
    cursor_y = int(mapy / 2);
    gfx_FillScreen(BG_color);
    gfx_SetTextBGColor(BG_color);
    clear_map();
    make_map();
    draw_map();
    draw_cursor();
}

void lose_round(){
    gfx_SetTextXY(1, 1);
    gfx_SetTextFGColor(0b11100000);
    gfx_SetTextBGColor(0b11111111);
    gfx_PrintString("You lose!");
}

void win_round(){
    gfx_SetTextXY(1, 1);
    gfx_SetTextFGColor(0b00000011);
    gfx_SetTextBGColor(0b11111111);
    gfx_PrintString("You win!");
}

uint8_t do_round(){
    unsigned int frame_start = clock();
    unsigned short frame_ms = 500;

    while(true){
        frame_start = clock();
        key = os_GetCSC();

        if(key == sk_Left && cursor_x > 0){
            clear_cursor();
            cursor_x -= 1;
        }
        if(key == sk_Right && cursor_x < mapx - 1){
            clear_cursor();
            cursor_x += 1;
        }
        if(key == sk_Up && cursor_y > 0){
            clear_cursor();
            cursor_y -= 1;
        }
        if(key == sk_Down && cursor_y < mapy - 1){
            clear_cursor();
            cursor_y += 1;
        }
        if(key == sk_Mode){
            draw_flag();
        }
        if(key == sk_2nd){
            if(map[cursor_x][cursor_y] == 10){
                return 0;
            }
            dig_xy(cursor_x, cursor_y);
        }
        if(boot_CheckOnPressed()){
            // If the 'ON' button is pressed
            return 3;
        }
        draw_cursor();
        //gfx_SwapDraw();

        while((clock() - frame_start) / 10 < frame_ms);
        
        if(clicks >= mapx * mapy - bomb_count){
            return 1;
        }
    }
}

int main(void){
    srand(rtc_Time());
    gfx_Begin();

    init_round();

    bool playing = true;

    while (playing){
        uint8_t enum_thing = do_round();
        if(enum_thing == 3){
            playing = false;
            break;
        }else if(enum_thing == 1){
            win_round();
        }else{
            lose_round();
        }
        unsigned int start = clock();
        while(clock() - start < 50000);
        init_round();
    }

    /* Return 0 for success */
    gfx_End();
    return 0;
}
