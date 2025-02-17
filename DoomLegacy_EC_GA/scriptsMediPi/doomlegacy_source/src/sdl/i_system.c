// Emacs style mode select   -*- C++ -*-
//-----------------------------------------------------------------------------
//
// $Id: i_system.c 1624 2022-04-03 22:06:03Z wesleyjohnson $
//
// Copyright (C) 1993-1996 by id Software, Inc.
// Copyright (C) 1998-2022 by DooM Legacy Team.
//
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
//
// $Log: i_system.c,v $
// Revision 1.12  2003/05/04 04:24:08  sburke
// Add Solaris support.
//
// Revision 1.11  2002/01/03 19:20:07  bock
// Add FreeBSD code to I_GetFreeMem.
// Modified Files:
//     makefile linux_x/i_system.c sdl/i_system.c
//
// Revision 1.10  2001/12/31 16:56:39  metzgermeister
// see Dec 31 log
//
// Revision 1.9  2001/08/20 20:40:42  metzgermeister
//
// Revision 1.8  2001/05/16 22:33:35  bock
// Initial FreeBSD support.
//
// Revision 1.7  2001/03/12 21:03:10  metzgermeister
//   * new symbols for rendererlib added in SDL
//   * console printout fixed for Linux&SDL
//   * Crash fixed in Linux SW renderer initialization
//
// Revision 1.6  2001/02/24 13:35:23  bpereira
// Revision 1.5  2000/11/02 19:49:40  bpereira
// Revision 1.4  2000/10/16 21:20:53  hurdler
//
// Revision 1.3  2000/09/26 17:58:06  metzgermeister
// I_Getkey implemented
//
// Revision 1.2  2000/09/10 10:56:00  metzgermeister
// Revision 1.1  2000/08/21 21:17:32  metzgermeister
// Initial import to CVS
//
//
// DESCRIPTION:
//   SDL system interface
//
//-----------------------------------------------------------------------------

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

#include <SDL.h>


#ifdef LINUX
# ifdef FREEBSD
#  include <sys/param.h>
#  include <sys/mount.h>
   // meminfo
#  include <sys/types.h>
#  include <sys/sysctl.h>
# elif defined( __MACH__ ) || defined( NETBSD )
#  include <sys/statvfs.h>
# else
#  include <sys/vfs.h>
# endif
#endif

#ifdef __MACH__
# include <mach-o/dyld.h>
  // _NSGetExecutablePath
#endif

#include <libgen.h>
  // dirname function

#include "doomincl.h"
#include "m_misc.h"
#include "screen.h"
#include "i_video.h"
#include "i_sound.h"
#include "i_system.h"

#include "d_net.h"
#include "g_game.h"
#include "g_input.h"

#include "keys.h"
#include "i_joy.h"
#include "m_argv.h"


// MOUSE2_NIX dependent upon DoomLegacy headers.
#ifdef MOUSE2_NIX
# include <termios.h>
# include <sys/ioctl.h>
#endif

//#define DEBUG_MOUSEMOTION
  
//#define DEBUG_MOUSE2
//#define DEBUG_MOUSE2_STIMULUS



#ifdef SDL2
// New SDL2 calls need the window.
extern SDL_Window * sdl_window;
#endif


extern void D_PostEvent(event_t*);

// 4 joysticks should be enough for most purposes
#define MAX_JOYSTICKS 4
int num_joysticks = 0;
SDL_Joystick *joysticks[MAX_JOYSTICKS]; 


#ifdef XBOX_CONTROLLER
boolean check_Joystick_Xbox[ MAX_JOYSTICKS ] = {false, false, false, false};
#endif

//
//I_OutputMsg
//
void I_OutputMsg       (char *fmt, ...) 
{
    va_list     argptr;

    va_start (argptr,fmt);
    vfprintf (stderr,fmt,argptr);
    va_end (argptr);
}

//
// I_GetKey
//
int  I_GetKey(void)
{
    // Warning: I_GetKey empties the event queue till next keypress
    event_t * ev;
    int rc = 0;

    // return the first keypress from the event queue
    while (eventtail != eventhead)
    {
        ev = &events[eventtail];
        if(ev->type == ev_keydown)
        {
            rc = ev->data1;
        }

        eventtail++;
        eventtail = eventtail & (MAXEVENTS-1);
    }

    return rc;
}

#ifdef SDL2
// Indexed by SDL2 scancode/keycode.
// Starts at SDL_SCANCODE_CAPSLOCK
uint16_t sdl2_F_to_key[] = {
  KEY_CAPSLOCK, // SDL_SCANCODE_CAPSLOCK
  KEY_F1, // SDL_SCANCODE_F1
  KEY_F2, // SDL_SCANCODE_F2
  KEY_F3, // SDL_SCANCODE_F3
  KEY_F4, // SDL_SCANCODE_F4
  KEY_F5, // SDL_SCANCODE_F5
  KEY_F6, // SDL_SCANCODE_F6
  KEY_F7, // SDL_SCANCODE_F7
  KEY_F8, // SDL_SCANCODE_F8
  KEY_F9, // SDL_SCANCODE_F9
  KEY_F10, // SDL_SCANCODE_F10
  KEY_F11, // SDL_SCANCODE_F11
  KEY_F12, // SDL_SCANCODE_F12
  KEY_PRINT, // SDL_SCANCODE_PRINTSCREEN
  KEY_SCROLLLOCK, // SDL_SCANCODE_SCROLLLOCK
  KEY_PAUSE, // SDL_SCANCODE_PAUSE
  KEY_INS, // SDL_SCANCODE_INSERT
     // PC: insert on PC
     // MAC: help on some Mac keyboards (but sends code SDL_SCANCODE_INSERT, not SDL_SCANCODE_HELP)
  KEY_HOME, // SDL_SCANCODE_HOME
  KEY_PGUP, // SDL_SCANCODE_PAGEUP
  KEY_DELETE, // SDL_SCANCODE_DELETE
  KEY_END, // SDL_SCANCODE_END
  KEY_PGDN, // SDL_SCANCODE_PAGEDOWN

  KEY_RIGHTARROW, // SDL_SCANCODE_RIGHT
  KEY_LEFTARROW, // SDL_SCANCODE_LEFT
  KEY_DOWNARROW, // SDL_SCANCODE_DOWN
  KEY_UPARROW, // SDL_SCANCODE_UP

  KEY_NUMLOCK, // SDL_SCANCODE_NUMLOCKCLEAR
     // PC: num lock on PC
     // MAC: clear
  KEY_KPADSLASH, // SDL_SCANCODE_KP_DIVIDE
  KEY_KPADMULT, // SDL_SCANCODE_KP_MULTIPLY
  KEY_MINUSPAD, // SDL_SCANCODE_KP_MINUS
  KEY_PLUSPAD, // SDL_SCANCODE_KP_PLUS
  KEY_KPADENTER, // SDL_SCANCODE_KP_ENTER
  KEY_KEYPAD1, // SDL_SCANCODE_KP_1
  KEY_KEYPAD2, // SDL_SCANCODE_KP_2
  KEY_KEYPAD3, // SDL_SCANCODE_KP_3
  KEY_KEYPAD4, // SDL_SCANCODE_KP_4
  KEY_KEYPAD5, // SDL_SCANCODE_KP_5
  KEY_KEYPAD6, // SDL_SCANCODE_KP_6
  KEY_KEYPAD7, // SDL_SCANCODE_KP_7
  KEY_KEYPAD8, // SDL_SCANCODE_KP_8
  KEY_KEYPAD9, // SDL_SCANCODE_KP_9
  KEY_KEYPAD0, // SDL_SCANCODE_KP_0
  KEY_KPADPERIOD, // SDL_SCANCODE_KP_PERIOD
  KEY_NULL, // SDL_SCANCODE_NONUSBACKSLASH
  KEY_NULL, // SDL_SCANCODE_APPLICATION
  KEY_NULL, // SDL_SCANCODE_POWER
  KEY_KPADEQUALS, // SDL_SCANCODE_KP_EQUALS
};


// Indexed by SDL2 scancode/keycode.
// Starts at SDL_SCANCODE_LCTRL
uint16_t sdl2_C_to_key[] = {
  KEY_LCTRL, // SDL_SCANCODE_LCTRL
  KEY_LSHIFT, // SDL_SCANCODE_LSHIFT
  KEY_LALT,  // SDL_SCANCODE_LALT
    // alt, option
  KEY_LWIN, // SDL_SCANCODE_LGUI
    // windows, command (apple), meta
  KEY_RCTRL, // SDL_SCANCODE_RCTRL
  KEY_RSHIFT, // SDL_SCANCODE_RSHIFT
  KEY_RALT, // SDL_SCANCODE_RALT
    // alt gr, option
  KEY_RWIN, // SDL_SCANCODE_RGUI
    // windows, command (apple), meta
};

#endif
  

//
//  Translates the SDL key into Doom key
//
static uint16_t  xlatekey(uint32_t keycode)
{
  // leave ASCII codes unchanged, as well as most other SDL keys
#ifdef SDL2  
  if(keycode > SDLK_UNKNOWN)
  {
      // SDL ASCII keycode are 1 .. 127
      if(keycode <= 0x7F)
          return keycode;

      // Other keycode are scancode OR with 0x40000000
      keycode &= 0xFFFF;  // to scancode
      // Scancode upto SDLK_SCANCODE_MODE are ( 4 .. 257 )
      if((keycode >= SDL_SCANCODE_CAPSLOCK) && (keycode <= SDL_SCANCODE_KP_EQUALS))
          return sdl2_F_to_key[keycode - SDL_SCANCODE_CAPSLOCK];
      if((keycode >= SDL_SCANCODE_LCTRL) && (keycode <= SDL_SCANCODE_RGUI))
          return sdl2_C_to_key[keycode - SDL_SCANCODE_LCTRL];

      switch( keycode )
      {
       case SDL_SCANCODE_SYSREQ:
          return KEY_SYSREQ;
       case SDL_SCANCODE_HELP:
          return KEY_HELP;
       case SDL_SCANCODE_MENU:
          return KEY_MENU;
       case SDL_SCANCODE_MODE:
          return KEY_MODE;
      };
  }
#else
  // SDL 1.2
  // SDL keycode are 9 .. 322
  if (keycode > SDLK_UNKNOWN && keycode <= SDLK_MENU)
    return keycode;
#endif

  return KEY_NULL;
}


//! Translates a SDL joystick button to a doom key_input_e number.
static int Translate_Joybutton(Uint8 which, Uint8 button)
{
  if (which >= MAXJOYSTICKS) 
    which = MAXJOYSTICKS-1;

  if (button >= JOYBUTTONS)
    button = JOYBUTTONS-1;

  return KEY_JOY0BUT0 + JOYBUTTONS*which + button;
}

static int Translate_Joyhat(Uint8 which, Uint8 value)
{
  if (which >= MAXJOYSTICKS) 
    which = MAXJOYSTICKS-1;

  if(value == SDL_HAT_UP)
  {
    return KEY_JOY0HATUP + JOYHATBUTTONS*which;
  }
  else if(value == SDL_HAT_RIGHT)
  {
    return KEY_JOY0HATRIGHT + JOYHATBUTTONS*which;
  }
  else if(value == SDL_HAT_DOWN)
  {
    return KEY_JOY0HATDOWN + JOYHATBUTTONS*which;
  }
  else if(value == SDL_HAT_LEFT)
  {
    return KEY_JOY0HATLEFT + JOYHATBUTTONS*which;
  }
  else
  {
    return 0;
  }
}

#ifdef XBOX_CONTROLLER
static int Translate_Xbox_controller_Trigger(Uint8 which, Uint8 axis)
{
  if (which >= MAXJOYSTICKS) 
    which = MAXJOYSTICKS-1;
    
  if(axis == 2)
  {
    return KEY_JOY0LEFTTRIGGER + XBOXTRIGGERS*which;
  }
  else if(axis == 5)
  {
    return KEY_JOY0RIGHTTRIGGER + XBOXTRIGGERS*which;
  }
  else
  {
    return 0;
  }
}
#endif

int I_JoystickNumAxes(int joynum)
{
  if (joynum < num_joysticks)
    return SDL_JoystickNumAxes(joysticks[joynum]);
  else
    return 0;
}

int I_JoystickGetAxis(int joynum, int axisnum)
{
  if (joynum < num_joysticks)
    return SDL_JoystickGetAxis(joysticks[joynum], axisnum);
  else
    return 0;
}



static int vid_center_x = 100;
static int vid_center_y = 100;
static int mouse_x_min = 25;
static int mouse_x_max = 175;
static int mouse_y_min = 25;
static int mouse_y_max = 175;
static int lastmousex = 0;
static int lastmousey = 0;

// current modifier key status
// SDL uses modifier masks.
byte shiftdown = 0;
byte altdown = 0;

Uint8 jhat_directions[8] = {
  SDL_HAT_UP,
  SDL_HAT_RIGHTUP,
  SDL_HAT_RIGHT,
  SDL_HAT_RIGHTDOWN,
  SDL_HAT_DOWN,
  SDL_HAT_LEFTDOWN,
  SDL_HAT_LEFT,
  SDL_HAT_LEFTUP
};
Uint8 previous_jhat[2] = {0, 0};


// MOUSE2_NIX dependent upon DoomLegacy headers.
#ifdef MOUSE2_NIX
int mouse2_fd = -1;
byte mouse2_started = 0;
static void I_GetMouse2Event(void);
#endif
#ifdef MOUSE2_WIN
HANDLE mouse2_filehandle = 0;
static void I_GetMouse2Event(void);
#endif
#ifdef MOUSE2_DOS
HANDLE mouse2_filehandle = 0;
static void I_GetMouse2Event(void);
#endif
#ifdef DEBUG_MOUSE2_STIMULUS
// trigger mouse2 stimulus
static byte  mouse2_stim_trigger = 0;
#endif

void I_GetEvent(void)
{
  SDL_Event inputEvent;
#ifdef SDL2
  SDL_Keymod mod;
  SDL_Keycode keycode;
#else   
  SDLKey keycode;
  SDLMod mod;
#endif

  event_t event;

#ifdef MOUSE2_NIX
  if( mouse2_started )
      I_GetMouse2Event();
#endif
#ifdef MOUSE2_WIN
  if( mouse2_filehandle )
      I_GetMouse2Event();
#endif

  while (SDL_PollEvent(&inputEvent))
  {
      switch (inputEvent.type)
      {
        case SDL_KEYDOWN:
          event.type = ev_keydown;  // doomlegacy keydown event
          keycode = inputEvent.key.keysym.sym; // SDL keyboard
          event.data1 = xlatekey(keycode); // key symbol

          mod = inputEvent.key.keysym.mod; // modifier key states
          // this might actually belong in D_PostEvent
          shiftdown = mod & KMOD_SHIFT;
          altdown = ((mod & KMOD_ALT) >> 8 ) | (mod & KMOD_ALT);  // force into byte

#ifdef SDL2
          // SDL2 does not provide char translations in SDL_KEYDOWN.
          // SDL2 provides TEXTINPUT separately.
          event.data2 = 0; // non-ASCII char
//printf( "Key DOWN 0x%04x => D1=0x%04x D2=0x%04x  |%c|\n", keycode, event.data1, event.data2, event.data1 );
#else
          // Corresponding ASCII char, if applicable (for console etc.)
          // NOTE that SDL handles international keyboards and shift maps for us!
          Uint16 unicode = inputEvent.key.keysym.unicode; // SDL uses UCS-2 encoding (or maybe UTF-16?)
          event.data2 = ((unicode & 0xff80) == 0) ?
              unicode & 0x7F
            : 0; // non-ASCII char
#endif

#ifdef DEBUG_MOUSE2_STIMULUS
          // Intercept some keys and fake the mouse2 input using mouse2_stim_trigger.
          if( (event.data1 >= KEY_KEYPAD1) && (event.data1 <= KEY_KEYPAD9) )
          {
              mouse2_stim_trigger = event.data1 - KEY_KEYPAD0;
              break;
          }
#endif

          D_PostEvent(&event);
          break;

        case SDL_KEYUP:
          event.type = ev_keyup;
          keycode = inputEvent.key.keysym.sym; // SDL keyboard
          event.data1 = xlatekey(keycode);

          mod = inputEvent.key.keysym.mod; // modifier key states
          shiftdown = mod & KMOD_SHIFT;
          altdown = ((mod & KMOD_ALT) >> 8 ) | (mod & KMOD_ALT);  // force into byte

          D_PostEvent(&event);
          break;

#ifdef SDL2
        case SDL_TEXTINPUT:
          // SDL2 provides TEXT input, but DoomLegacy wants ASCII one keypress at a time.
          event.type = ev_keydown;
          event.data1 = 0x02;  // STX, dummy non-zero key (must be < KEY_NUMKB)
          event.data2 = ((inputEvent.text.text[0] & 0xff80) == 0)?
              inputEvent.text.text[0] & 0xFF
            : 0; // non-ASCII char
//printf( "Key TEXT= 0x%x 0x%x => D1=0x%04x D2=0x%04x  |%c|\n", inputEvent.text.text[0], inputEvent.text.text[1], event.data1, event.data2, event.data2 );
          D_PostEvent(&event);
          break;
#endif

        case SDL_MOUSEMOTION:
          if(cv_usemouse[0].EV)
          {
              event.type = ev_mouse;
              event.data1 = 0;
              // [WDJ] 8/2012 Some problems with Absolute mouse motion in OpenBSD.
              // Could not predict which would work best for a particular port,
              // so both are here, selected from mouse menu.
              if( cv_mouse_motion.value )
              {
                  // Relative mouse motion interface.
                  // Seems to be used by prboom and some other SDL Doom ports.
                  // SDL 2001 docs: Windows and Linux, otherwise don't know.
                  // Requires that SDL xrel and yrel report motion even when
                  // abs mouse position is limited at window border by grabinput.
                  // Linux: rel motion continues even when abs motion stopped by grabinput.
                  // OpenBSD: seems to work except when grabinput=0.
#ifdef DEBUG_MOUSEMOTION
                  fprintf(stderr, "Mouse %i,%i, rel %i,%i\n",
                      inputEvent.motion.x, inputEvent.motion.y,
                      inputEvent.motion.xrel, inputEvent.motion.yrel);
#endif
                  // y is negated because screen + is down, but map + is up.
                  event.data2 = inputEvent.motion.xrel << 2;
                  event.data3 = - (inputEvent.motion.yrel << 2);
              }
              else
              {
                  // Absolute mouse motion interface.  Default.
                  // Linux: works in all combinations.
                  // Windows: works, untested on newer
                  // OpenBSD: works, except that when grabinput=0 mouse
                  // cannot escape window.
#ifdef DEBUG_MOUSEMOTION
                  fprintf(stderr, "Mouse %i,%i,  old %i,%i,  rel %i,%i\n",
                      inputEvent.motion.x, inputEvent.motion.y,
                      lastmousex, lastmousey,
                      inputEvent.motion.x - lastmousex, inputEvent.motion.y - lastmousey);
#endif
                  // First calc relative motion using lastmouse,
                  // so can save lastmouse before WarpMouse test
                  event.data2 = (inputEvent.motion.x - lastmousex) << 2;
                  lastmousex = inputEvent.motion.x;
                  // y is negated because screen + is down, but map + is up.
                  event.data3 = (lastmousey - inputEvent.motion.y) << 2;
                  lastmousey = inputEvent.motion.y;
              }
#ifdef DEBUG_WINDOWED
              // DEBUG_WINDOWED blocks grabinput effects to get easy access to
              // debugging window, so it always needs WarpMouse.
#else
              // With Relative mouse motion and input grabbed,
              // SDL will limit range with (xrel, yrel) still working
              // Known to work on Linux, OpenBSD, and Windows.
              // Absolute mouse motion requires WarpMouse centering always.
              // Keyboard will be affected by grabinput, independently of this.
              if( (cv_mouse_motion.value==0) || ! cv_grabinput.value )
#endif
              {
                  static byte lastmouse_warp = 0;
                  // If the event is from warping the pointer back to middle
                  // of the screen then ignore it.  Not often, 45 degree turn.
                  if (lastmouse_warp
                      && (inputEvent.motion.x == vid_center_x)
                      && (inputEvent.motion.y == vid_center_y) )
                  {
                      lastmouse_warp = 0;
                      break;  // skip PostEvent
                  }

                  // Warp the pointer back to the middle of the window
                  //  or we cannot move any further when it reaches a border.
                  if ((inputEvent.motion.x < mouse_x_min) ||
                      (inputEvent.motion.y < mouse_y_min) ||
                      (inputEvent.motion.x > mouse_x_max) ||
                      (inputEvent.motion.y > mouse_y_max)   )
                  {
                      // Warp the pointer back to the middle of the window
#ifdef SDL2
                      SDL_WarpMouseInWindow( sdl_window, vid_center_x, vid_center_y);
//                      SDL_WarpMouseGlobal(vid_center_x, vid_center_y);
#else
                      SDL_WarpMouse(vid_center_x, vid_center_y);
#endif
                      // this issues a mouse event that needs to be ignored
                      lastmouse_warp = 1;
                  }
              }
              // issue mouse event
              D_PostEvent(&event);
          }
          break;

        case SDL_MOUSEBUTTONDOWN:
        case SDL_MOUSEBUTTONUP:
          if(cv_usemouse[0].EV)
          {
              if (inputEvent.type == SDL_MOUSEBUTTONDOWN)
                event.type = ev_keydown;
              else
                event.type = ev_keyup;

              event.data1 = KEY_MOUSE1 + inputEvent.button.button - SDL_BUTTON_LEFT;
              event.data2 = 0; // does not correspond to any character
              D_PostEvent(&event);
          }
          break;

        case SDL_JOYBUTTONDOWN:
          event.type = ev_keydown;
          event.data1 = Translate_Joybutton(inputEvent.jbutton.which,
                                           inputEvent.jbutton.button);
          event.data2 = 0;
          D_PostEvent(&event);
          break;

        case SDL_JOYBUTTONUP:
          event.type = ev_keyup;
          event.data1 = Translate_Joybutton(inputEvent.jbutton.which,
                                           inputEvent.jbutton.button);
          event.data2 = 0;
          D_PostEvent(&event);
          break;

        case SDL_JOYHATMOTION: // Adding event to allow joy hat mapping
          // [Leonardo Montenegro]
          event.data2 = 0;
          if(inputEvent.jhat.value != SDL_HAT_CENTERED)
          {
              // Joy hat pressed

              // Releasing previous value
              int i;
              for(i=0; i<2; i++)
              {
                  if(previous_jhat[i] != 0)
                  {
                      event.type = ev_keyup;
                      event.data1 = Translate_Joyhat(inputEvent.jhat.which, previous_jhat[i]);
                      D_PostEvent(&event);

                      previous_jhat[i] = 0;
                  }
              }

              // Dealing with diagonal directions
              if(inputEvent.jhat.value == SDL_HAT_RIGHTUP)
              {
                  event.type = ev_keydown;
                  event.data1 = Translate_Joyhat(inputEvent.jhat.which, SDL_HAT_RIGHT);
                  D_PostEvent(&event);
                  previous_jhat[0] = SDL_HAT_RIGHT;

                  event.type = ev_keydown;
                  event.data1 = Translate_Joyhat(inputEvent.jhat.which, SDL_HAT_UP);
                  D_PostEvent(&event);
                  previous_jhat[1] = SDL_HAT_UP;
              }
              else if(inputEvent.jhat.value == SDL_HAT_RIGHTDOWN)
              {
                  event.type = ev_keydown;
                  event.data1 = Translate_Joyhat(inputEvent.jhat.which, SDL_HAT_RIGHT);
                  D_PostEvent(&event);
                  previous_jhat[0] = SDL_HAT_RIGHT;

                  event.type = ev_keydown;
                  event.data1 = Translate_Joyhat(inputEvent.jhat.which, SDL_HAT_DOWN);
                  D_PostEvent(&event);
                  previous_jhat[1] = SDL_HAT_DOWN;
              }
              else if(inputEvent.jhat.value == SDL_HAT_LEFTDOWN)
              {
                  event.type = ev_keydown;
                  event.data1 = Translate_Joyhat(inputEvent.jhat.which, SDL_HAT_LEFT);
                  D_PostEvent(&event);
                  previous_jhat[0] = SDL_HAT_LEFT;

                  event.type = ev_keydown;
                  event.data1 = Translate_Joyhat(inputEvent.jhat.which, SDL_HAT_DOWN);
                  D_PostEvent(&event);
                  previous_jhat[1] = SDL_HAT_DOWN;
              }
              else if(inputEvent.jhat.value == SDL_HAT_LEFTUP)
              {
                  event.type = ev_keydown;
                  event.data1 = Translate_Joyhat(inputEvent.jhat.which, SDL_HAT_LEFT);
                  D_PostEvent(&event);
                  previous_jhat[0] = SDL_HAT_LEFT;

                  event.type = ev_keydown;
                  event.data1 = Translate_Joyhat(inputEvent.jhat.which, SDL_HAT_UP);
                  D_PostEvent(&event);
                  previous_jhat[1] = SDL_HAT_UP;
              }
              else
              {
                  event.type = ev_keydown;
                  event.data1 = Translate_Joyhat(inputEvent.jhat.which, inputEvent.jhat.value);
                  D_PostEvent(&event);

                  previous_jhat[0] = inputEvent.jhat.value;
              }
          }
          else
          {
              // Joy hat released
              int i;
              for(i=0; i<8; i++)
              {
                  event.type = ev_keyup;
                  event.data1 = Translate_Joyhat(inputEvent.jhat.which, jhat_directions[i]);
                  D_PostEvent(&event);
              }

              previous_jhat[0] = 0;
              previous_jhat[1] = 0;
          }
          break;

#ifdef XBOX_CONTROLLER
        case SDL_JOYAXISMOTION: // Adding event for mapping triggers for Xbox-like controllers
          // [Leonardo Montenegro]
          if(check_Joystick_Xbox[inputEvent.jaxis.which])
          {
              if(inputEvent.jaxis.axis == 2 || inputEvent.jaxis.axis == 5)
              {
                  event.data2 = 0;
                  if(inputEvent.jaxis.value > 0)
                  {
                      // Trigger pressed
                      event.type = ev_keydown;
                      event.data1 = Translate_Xbox_controller_Trigger(inputEvent.jaxis.which, inputEvent.jaxis.axis);
                      D_PostEvent(&event);
                  }
                  else
                  {
                      // Trigger released
                      event.type = ev_keyup;
                      event.data1 = Translate_Xbox_controller_Trigger(inputEvent.jaxis.which, inputEvent.jaxis.axis);
                      D_PostEvent(&event);
                  }
              }
          }
          break;
#endif
 
        case SDL_QUIT:
          I_Quit();
          //M_QuitResponse('y');
          break;

        default:
          break;
      }
  }
}


// [WDJ] 8/2012 Grab mouse re-enabled as option menu item.

static void I_GrabMouse(void)
{
  if( cv_grabinput.value && !devparm )
  {
#ifdef DEBUG_WINDOWED
         // do not grab so can use debugger
#else
      // Grab the mouse
#ifdef SDL2
      if( ! SDL_GetWindowGrab( sdl_window ) )
      {
         SDL_SetWindowGrab( sdl_window, 1 );
      }
#else
      // SDL 1.2	  
      if(SDL_GRAB_OFF == SDL_WM_GrabInput(SDL_GRAB_QUERY))
      {
         SDL_WM_GrabInput(SDL_GRAB_ON);
      }
#endif
#endif
  }
}

void I_UngrabMouse(void)
{
#ifdef SDL2
  if( SDL_GetWindowGrab( sdl_window ) )
  {
      SDL_SetWindowGrab( sdl_window, 0 );
  }
#else
  if(SDL_GRAB_ON == SDL_WM_GrabInput(SDL_GRAB_QUERY))
  {
      SDL_WM_GrabInput(SDL_GRAB_OFF);
  }
#endif
}

// Called on video mode change, usemouse change, mousemotion change,
// and game paused.
//   play_mode : enable mouse containment during play
void I_StartupMouse( boolean play_mode )
{
    vid_center_x = vid.width >> 1;
    vid_center_y = vid.height >> 1;
    lastmousex = vid_center_x;
    lastmousey = vid_center_y;
    if( cv_usemouse[0].EV && play_mode )
    {
        // Enable mouse containment during play.
        SDL_Event inputEvent;
        // warp to center
#ifdef SDL2
        SDL_WarpMouseInWindow( sdl_window, vid_center_x, vid_center_y);
#else
        SDL_WarpMouse(vid_center_x, vid_center_y);
#endif
        // remove the mouse event by reading the queue
        SDL_PollEvent(&inputEvent);

        // Guard band at window border: 20%=51, 25%=64, 30%=76
        mouse_x_min = (vid.width * 64) >> 8;
        mouse_x_max = vid.width - mouse_x_min;
        mouse_y_min = (vid.height * 64) >> 8;
        mouse_y_max = vid.height - mouse_y_min;

        I_GrabMouse();
    }
    else
    {
        // Disable Guard band.
        mouse_x_min = -1;
        mouse_x_max = 20000;
        mouse_y_min = -1;
        mouse_y_max = 20000;

        I_UngrabMouse();
    }
    return;
}


/// Initialize joysticks and print information.
static void I_JoystickInit(void)
{
  // Joystick subsystem was initialized at the same time as video,
  // because otherwise it won't work. (don't know why, though ...)

  num_joysticks = min(MAX_JOYSTICKS, SDL_NumJoysticks());
  CONS_Printf(" %d joystick(s) found.\n", num_joysticks);

  // Start receiving joystick events.
  SDL_JoystickEventState(SDL_ENABLE);

  int i;
  for (i=0; i < num_joysticks; i++)
  {
      SDL_Joystick *joy = SDL_JoystickOpen(i);
#ifdef SDL2
      const char * jname = SDL_JoystickNameForIndex(i);
#else
      const char * jname = SDL_JoystickName(i);
#endif
      joysticks[i] = joy;
      if (devparm || verbose > 1)
      {
          CONS_Printf(" Properties of joystick %d:\n", i);
          if( jname )  CONS_Printf("    %s.\n", jname);
          CONS_Printf("    %d axes.\n", SDL_JoystickNumAxes(joy));
          CONS_Printf("    %d buttons.\n", SDL_JoystickNumButtons(joy));
          CONS_Printf("    %d hats.\n", SDL_JoystickNumHats(joy));
          CONS_Printf("    %d trackballs.\n", SDL_JoystickNumBalls(joy));
      }
      
#ifdef XBOX_CONTROLLER     
      check_Joystick_Xbox[i] = jname &&
        (  strcmp(jname, "Xbox 360 Wireless Receiver (XBOX)") == 0
        || strcmp(jname, "Microsoft X-Box 360 pad") == 0  );
#endif     
  }
}


/// Close all joysticks.
static void I_ShutdownJoystick(void)
{
  CONS_Printf("Shutting down joysticks.\n");
  int i;
  for(i=0; i < num_joysticks; i++)
  {
#ifdef SDL2
    const char * jname = SDL_JoystickNameForIndex(i);
#else
    const char * jname = SDL_JoystickName(i);
#endif
    if( jname )  CONS_Printf("Closing joystick %s.\n", jname);
    SDL_JoystickClose(joysticks[i]);
    joysticks[i] = NULL;
  }
  
  CONS_Printf("Joystick subsystem closed cleanly.\n");
}


/// initialize SDL
void I_SysInit(void)
{
  CONS_Printf("Initializing SDL...\n");

  // Initialize Audio as well, otherwise DirectX can not use audio
  if( SDL_Init(SDL_INIT_AUDIO | SDL_INIT_VIDEO | SDL_INIT_JOYSTICK) != 0 )
  {
      CONS_Printf(" Couldn't initialize SDL: %s\n", SDL_GetError());
      D_Quit_Save( QUIT_shutdown );
      I_Quit_System();
  }

#ifdef SDL2
#else
  // SDL 1.2
  // Window title
  SDL_WM_SetCaption(VERSION_BANNER, "Doom Legacy");

  // Enable unicode key conversion
  SDL_EnableUNICODE(1);
#endif

  // Initialize the joystick subsystem.
  I_JoystickInit();
}


//
// I_OsPolling
//
void I_OsPolling(void)
{
  if ( graphics_state == VGS_off )
    return;

  I_GetEvent();
}


//
// I_GetMouse2Event
//

#ifdef MOUSE2

#ifdef DEBUG_MOUSE2
static void  dump_packet( const char * msg, byte * packet, int len )
{
    char  bb[128];
    int   bn = 0;
    int   i;

    if( len > 127 )  len=127;
    for( i=0; i<len; i++ )
        bn += snprintf( &bb[bn], 128-bn, " %X", packet[i] );
    bb[127] = 0;
    CONS_Printf( "%s len=%i : %s\n", msg, len, bb );
}
#endif

#ifdef DEBUG_MOUSE2_STIMULUS
const byte PC_stim[] = {
 0x40, 0x04, 0x00, 0x40, 0x10, 0x00, 0x40, 0x08, 0x00, 0x41, 0x00, 0x00,
 0x43, 0x31, 0x00, 0x43, 0x20, 0x00, 0x43, 0x28, 0x00, 0x43, 0x21, 0x00,
 0x40, 0x00, 0x10, 0x40, 0x00, 0x20, 0x40, 0x00, 0x1F, 0x44, 0x00, 0x00,
 0x4C, 0x00, 0x3F, 0x4C, 0x00, 0x32, 0x4C, 0x00, 0x31, 0x4C, 0x00, 0x20,
 0x60, 0x00, 0x00, 0x40, 0x00, 0x00, 0x50, 0x00, 0x00, 0x40, 0x00, 0x00,
};
const byte PC_stim_len = 12;
const byte PC_stim_index[] = { 0, 0, 12, 24, 36, 48, 3, 15, 18, 48, 0 };
#endif


#define MOUSE2_BUFFER_SIZE 256

// This table converts PC-Mouse button order (LB, RB)
// to our internal button order (B3, B2, B1).
// Converts  (LB, RB) ==> (RB, CB, LB)
const byte PC_Mouse_to_button[4] = {0,4,1,5};

// This table converts MouseSystems button order (LB, CB, RB)
// to our internal button order (B3, B2, B1).
// Converts  (LB, CB, RB) ==> (RB, CB, LB)
//const byte MouseSystems_to_button[8] = {0,4,2,6,1,5,3,7}; // true high
const byte MouseSystems_to_button[8] = {7,3,5,1,6,2,4,0}; // true low

// Converts  (MB, RB, LB) ==> (RB, CB, LB)
const byte PS2_to_button[8] = {0,1,4,5,2,3,6,7};

static void I_GetMouse2Event()
{
    // The system update of the serial ports is slow and there may be 15 to 30 calls
    // before the next data read is ready.
    // We may get an incomplete mouse packet, the partial packet is kept in m2pkt.
    static int   m2plen = 7;  // mouse2 packet length
    static byte  m2pkt[8];    // mouse2 packet
    static byte  mouse2_ev_buttons = 0;
    static byte  staleness = 0;

    event_t event;

    // System read is expensive, so read to buffer, and process all of it.
    byte m2_buffer[MOUSE2_BUFFER_SIZE];
    int  m2_len;
    int  m2i;
    int  mouse2_rd_x, mouse2_rd_y;
    byte  mouse2_rd_buttons;

#ifdef DEBUG_MOUSE2_STIMULUS
    if( cv_mouse2type.EV == 0 )
    {
        if( staleness < 15 )  goto no_input;
        if( mouse2_stim_trigger == 0 )  goto no_input;
        if( cv_mouse2type.EV == 0 )
        {
            memcpy( m2_buffer, &PC_stim[ PC_stim_index[mouse2_stim_trigger]], PC_stim_len );
            m2_len = PC_stim_len;
        }
        mouse2_stim_trigger = 0;
        goto got_packet;
    }
#endif
   
#ifdef MOUSE2_NIX
  {
    // Fill m2_buffer, without knowing start of packet.
    m2_len = read(mouse2_fd, m2_buffer, MOUSE2_BUFFER_SIZE);
    if( m2_len < 1 )
        goto no_input;
  }
#endif

#ifdef MOUSE2_WIN
  {
    COMSTAT    ComStat ;
    DWORD      dwErrorFlags;
    DWORD      dwLength;

    ClearCommError( mouse2_filehandle, &dwErrorFlags, &ComStat ) ;
    dwLength = min( MOUSE2_BUFFER_SIZE, ComStat.cbInQue ) ;

    if( dwLength <= 0 )
        goto no_input;

    if(!ReadFile( mouse2_filehandle, m2_buffer, dwLength, &dwLength, NULL ))
    {
        CONS_Printf("\2Read Error on secondary mouse port\n");
        goto no_input;
    }
    m2_len = dwLength;
  }
#endif

#ifdef DEBUG_MOUSE2_STIMULUS
got_packet:
#endif
       
#ifdef DEBUG_MOUSE2
    CONS_Printf("staleness= %i \n", staleness);
    if( m2plen > 0 && m2plen < 5 )
    {
       dump_packet(" leftover", m2pkt, m2plen );
    }
    dump_packet( "mouse buffer", m2_buffer, m2_len );
#endif

    // Defer processing inits, most often will not have any input.
    staleness = 0;
    mouse2_rd_buttons = mouse2_ev_buttons; // to detect changes
    mouse2_rd_x = mouse2_rd_y = 0;

    // Mouse packets can be 3 or 4 bytes.
    // Parse the mouse packets
    for(m2i=0; m2i<m2_len; m2i++)
    {
        byte mb = m2_buffer[m2i];

        // Sync detect
        switch( cv_mouse2type.EV )
        {
          case 0:  // PC Mouse
            if( mb & 0x40 )  // first byte
                m2plen = 0;
            break;

          case 1:  // MouseSystems
            if( (m2plen >= 5) && (mb & 0x80) )  // first byte
                m2plen = 0;
            break;

          case 2:  // PS/2
            if( (m2plen >= 3) && (mb & 0x04) )  // maybe first byte
                m2plen = 0;
            break;

#if 0	     
          default: // no sync detect, count bytes
            if( m2plen >= 3 )
                m2plen = 0;
            break; 
#endif
        }
            
        if(m2plen > 6)  continue;
            
#ifdef DEBUG_MOUSE2
        CONS_Printf( " m2pkt[%i]= %X = m2_buffer[%i]\n", m2plen, mb, m2i);
#endif
        m2pkt[m2plen++] = mb;

        switch( cv_mouse2type.EV )
        {
          case 0:  // PC Mouse
            if(m2plen==3)
            {
#ifdef DEBUG_MOUSE2
                dump_packet( "PC", m2pkt, 3 );
#endif
                // PC mouse format, Microsoft protocol, 2 buttons.
                mouse2_rd_buttons &= ~0x05; // B1, B3
                mouse2_rd_buttons |= PC_Mouse_to_button[ (m2pkt[0] & 0x30) >> 4];  // RB, LB
                int dx = (int8_t)(((m2pkt[0] & 0x03) << 6) | (m2pkt[1] & 0x3F)); // signed
                int dy = (int8_t)(((m2pkt[0] & 0x0C) << 4) | (m2pkt[2] & 0x3F)); // signed
#ifdef DEBUG_MOUSE2
                CONS_Printf( "mouse buttons= %X  dx,dy = ( %i, %i )\n", mouse2_rd_buttons, dx, dy);
#endif
                mouse2_rd_x += (int) dx;
                mouse2_rd_y += (int) dy;
                goto post_event;
            }
            else if(m2plen==4) // fourth byte (logitech mouses)
            {
                 // Logitech extension to Microsoft protocol
                 // This is only sent when CB is pressed.
                mouse2_rd_buttons &= ~0x02;
                mouse2_rd_buttons |= (m2pkt[3] & 0x20) >> 4; // CB => B2
#ifdef DEBUG_MOUSE2
                CONS_Printf( "mouse Logitech buttons %i\n", mouse2_rd_buttons);
#endif
                goto post_event;
            }
            continue;

          case 1:  // MouseSystems
            if(m2plen==5)
            {
#ifdef DEBUG_MOUSE2
                dump_packet( "MS", m2pkt, 5 );
#endif
                // MouseSystems mouse buttons
                mouse2_rd_buttons = MouseSystems_to_button[m2pkt[0] & 0x07];  // true low
                // MouseSystems mouse movement
                int dx = (int8_t)(m2pkt[1]);
                int dy = (int8_t)(m2pkt[2]);
                dx += (int8_t)(m2pkt[3]);
                dy += (int8_t)(m2pkt[4]);
#ifdef DEBUG_MOUSE2
                CONS_Printf( "mouse buttons= %X  dx,dy = ( %i, %i )\n", mouse2_rd_buttons, dx, dy);
#endif
                mouse2_rd_x += dx;
                mouse2_rd_y += dy;
                goto post_event;
            }
            continue;

          case 3:  // PS/2
            if(m2plen==3)
            {
#ifdef DEBUG_MOUSE2
                dump_packet( "PS2", m2pkt, 3 );
#endif
                // PS/2 mouse buttons
                mouse2_rd_buttons = PS2_to_button[m2pkt[0] & 0x07];
                // PS/2 mouse movement
                int dx = (int8_t)((m2pkt[0] & 0x10)<<3);  // signed
                int dy = (int8_t)((m2pkt[0] & 0x20)<<2);  // signed
                dx = (dx<<1) | m2pkt[1];
                dy = (dy<<1) | m2pkt[2];
#ifdef DEBUG_MOUSE2
                CONS_Printf( "mouse buttons= %X  dx,dy = ( %i, %i )\n", mouse2_rd_buttons, dx, dy);
#endif
                mouse2_rd_x += dx;
                mouse2_rd_y += dy;
                goto post_event;
            }
            continue;
        } // switch
        continue;

    post_event:
       {
        // Post mouse2 events
        byte mbk = (mouse2_rd_buttons ^ mouse2_ev_buttons); // changed buttons
        if( mbk )  // button changed, infrequent
        {
            mouse2_ev_buttons = mouse2_rd_buttons;

            int k;
            for(k=0; mbk; k++, mbk>>=1)  // until have processed all changed buttons
            {
                if(mbk & 0x01)  // button changed
                {
                    byte mbm = 1<<k;
                    event.type = (mouse2_rd_buttons & mbm)? ev_keydown : ev_keyup;
                    event.data1= KEY_MOUSE2+k;
                    event.data2= 0;  // must for ev_keydown
                    D_PostEvent(&event);
                }
#ifdef DEBUG_MOUSE2
                if( k > 5 )
                {
                    CONS_Printf("Mouse2 button in tight-loop\n");
                    break;
                }
#endif
            }
        }
       }
    }

    // Only post sum of mouse movement, as there is only one movement per tick anyway.
    if( mouse2_rd_x | mouse2_rd_y )  // any movement
    {
        event.type = ev_mouse2;
        event.data1 = 0;
        event.data2 = mouse2_rd_x;
        event.data3 = - mouse2_rd_y;
        D_PostEvent(&event);
    }

#ifdef DEBUG_MOUSE2xx
    if( m2plen > 0 && m2plen < 5 )
    {
       dump_packet("Exit leftover", m2pkt, m2plen );
    }
#endif

    return;

no_input:
    if( staleness < 127 )
    {
        if( ++staleness == 32 )
            m2plen = 7;  // clear leftover
    }

    return;
}
#endif



//
// I_ShutdownMouse2
//
#ifdef MOUSE2_NIX
static void I_ShutdownMouse2_NIX(void)
{
  if(mouse2_fd!=-1) close(mouse2_fd);
  mouse2_started = 0;
}
#endif

#ifdef MOUSE2_WIN
static void I_ShutdownMouse2_WIN(void)
{
    if(mouse2_filehandle)
    {
        event_t event;
        int i;

        SetCommMask( mouse2_filehandle, 0 ) ;

        EscapeCommFunction( mouse2_filehandle, CLRDTR ) ;
        EscapeCommFunction( mouse2_filehandle, CLRRTS ) ;

        PurgeComm( mouse2_filehandle, PURGE_TXABORT | PURGE_RXABORT |
                                     PURGE_TXCLEAR | PURGE_RXCLEAR ) ;


        CloseHandle(mouse2_filehandle);

        // emulate the up of all mouse buttons
        for(i=0;i<MOUSEBUTTONS;i++)
        {
            event.type=ev_keyup;
            event.data1=KEY_MOUSE2+i;
            D_PostEvent(&event);
        }

        mouse2_filehandle=0;
    }
}
#endif

//
// I_StartupMouse2
// 
void I_StartupMouse2 (void)
{
#ifdef DEBUG_MOUSE2
    GenPrintf(EMSG_warn, "I_StartupMouse2\n");
#endif

#ifdef MOUSE2_NIX
// I_StartupMouse2_NIX (void)
    struct termios m2tio;
    int i;

    I_ShutdownMouse2_NIX();

    if(cv_usemouse[1].EV == 0)  return;

    #define M2PORT_LEN  24
    char m2port[M2PORT_LEN];
    snprintf( m2port, M2PORT_LEN-2, "/dev/%s", cv_mouse2port.string );
    m2port[M2PORT_LEN-1] = 0;
    mouse2_fd = open( m2port, O_RDONLY|O_NONBLOCK|O_NOCTTY );
    if(mouse2_fd == -1)
    {
        CONS_Printf("Error opening %s\n", m2port);
#ifdef DEBUG_MOUSE2_STIMULUS
        goto mouse2_stimulus;
#else
        return;
#endif
    }

    tcflush(mouse2_fd, TCIOFLUSH);
    m2tio.c_iflag = IGNBRK;
    m2tio.c_oflag = 0;
    m2tio.c_cflag = ( cv_mouse2type.EV == 0 )?
        CREAD|CLOCAL|HUPCL|CSTOPB|B1200 | CS7  // PC mouse
      : CREAD|CLOCAL|HUPCL|CSTOPB|B1200 | CS8; // MS and others
    m2tio.c_lflag = 0;
    m2tio.c_cc[VTIME] = 0;
    m2tio.c_cc[VMIN] = 1;
    tcsetattr(mouse2_fd, TCSANOW, &m2tio);

    // Determine DTR and RTS state from opt string.
    unsigned int  tiocm_0 = 0;
    unsigned int  tiocm_1 = 0;
    int optlen = strlen(cv_mouse2opt.string) - 1;  // need 2 char
    for(i=0; i< optlen; i++)
    {
        char c1 = cv_mouse2opt.string[i];
        char c2 = cv_mouse2opt.string[i+1];
        if( c1=='D' || c1=='d' )
        {
            if(c2 == '-')
                tiocm_0 |= TIOCM_DTR;  // DTR off
            else
                tiocm_1 |= TIOCM_DTR;  // DTR on
        }
        if( c1=='R' || c1=='r' )
        {
            if(c2 == '-')
                tiocm_0 |= TIOCM_RTS;  // RTS off
            else
                tiocm_1 |= TIOCM_RTS;  // RTS on
        }
    }
    // Set DTR and RTS
    if( tiocm_0 | tiocm_1 )
    {
        unsigned int tiocm_v;
        if(!ioctl(mouse2_fd, TIOCMGET, &tiocm_v)) {
            tiocm_v &= ~tiocm_0;  // DTR,RTS off
            tiocm_v |= tiocm_1;  // DTR,RTS on
            ioctl(mouse2_fd, TIOCMSET, &tiocm_v);
        }
    }
    mouse2_started = 1;
#endif

#ifdef MOUSE2_WIN
// I_StartupMouse2_WIN (void)
    // secondary mouse don't use directX, therefore forget all about grabing, acquire, etc...
    DCB        dcb ;

    I_ShutdownMouse2_WIN();

    if(cv_usemouse[1].EV == 0)  return;
   
    if(!mouse2_filehandle)
    {
#ifdef DEBUG_MOUSE2
        printf("Open Mouse2 device\n");
        GenPrintf(EMSG_warn, "Open Mouse2 device\n");
#endif

        // COM file handle
        mouse2_filehandle = CreateFile( cv_mouse2port.string, GENERIC_READ | GENERIC_WRITE,
                                       0,                     // exclusive access
                                       NULL,                  // no security attrs
                                       OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL );
        if( mouse2_filehandle == INVALID_HANDLE_VALUE )
        {
            const char * msg = "Error";
            int e=GetLastError();
            if( e==5 )  msg = "Access denied, may be in use";
            CONS_Printf("\2Can't open %s : %s.\n", cv_mouse2port.string, msg );
            mouse2_filehandle=0;
#ifdef DEBUG_MOUSE2_STIMULUS
            goto mouse2_stimulus;
#else
            return;
#endif
        }
    }
#ifdef DEBUG_MOUSE2
    printf("Setup Mouse2\n");
    GenPrintf(EMSG_warn, "Setup Mouse2\n");
#endif
    // getevent when somthing happens
    //SetCommMask( mouse2_filehandle, EV_RXCHAR ) ;
    
    // buffers
    SetupComm( mouse2_filehandle, MOUSE2_BUFFER_SIZE, MOUSE2_BUFFER_SIZE ) ;
    
    // purge buffers
    PurgeComm( mouse2_filehandle, PURGE_TXABORT | PURGE_RXABORT |
                                 PURGE_TXCLEAR | PURGE_RXCLEAR ) ;

    // setup port to 1200 7N1
    dcb.DCBlength = sizeof( DCB ) ;

    GetCommState( mouse2_filehandle, &dcb ) ;

    dcb.BaudRate = CBR_1200;
    // PC mouse is 7-bit, others are 8-bit
//    dcb.ByteSize = 7;
//    dcb.ByteSize = 8;
    dcb.ByteSize = (cv_mouse2type.EV == 0)? 7 : 8;

    dcb.Parity = NOPARITY ;
    dcb.StopBits = ONESTOPBIT ;

    dcb.fDtrControl = DTR_CONTROL_ENABLE ;
    dcb.fRtsControl = RTS_CONTROL_ENABLE ;

    dcb.fBinary = TRUE ;
    dcb.fParity = TRUE ;

    SetCommState( mouse2_filehandle, &dcb ) ;

    I_AddExitFunc (I_ShutdownMouse2_WIN);
#endif
   
   
#ifdef DEBUG_MOUSE2_STIMULUS
mouse2_stimulus:
    if( cv_mouse2type.EV == 0 )
    {
        // Enable mouse2 for fake input.        
#ifdef MOUSE2_NIX
        mouse2_started = 1;
#endif
#ifdef MOUSE2_WIN
        mouse2_filehandle = 5; // fake, but effective
#endif
        return;
    }
#endif

    return;
}



byte     mb_used = 6+2; // 2 more for caching sound

//
// I_Tactile
//
void I_Tactile(int on,int off,int total )
{
  // UNUSED.
  on = off = total = 0;
}

ticcmd_t        emptycmd;

ticcmd_t*       I_BaseTiccmd(void)
{
    return &emptycmd;
}

//
// I_GetTime
// returns time in 1/TICRATE second tics
//
tic_t I_GetTime(void)
{
    Uint32        ticks;
    static Uint32 basetime=0;

    // milliseconds since SDL initialization
    ticks = SDL_GetTicks();

    if (!basetime)
        basetime = ticks;

    return (ticks - basetime)*TICRATE/1000;
}

// sleeps for a while, giving CPU time to other processes
// in milleseconds
void I_Sleep(unsigned int ms)
{
  SDL_Delay(ms);
}


void shutdown_logmessage( const char * who, const char * msg );


// The final part of I_Quit, system dependent.
void I_Quit_System (void)
{
#ifdef LOGMESSAGES
    shutdown_logmessage( "I_Quit()", "end of logstream" );
#endif

    exit(0);
}


//
// I_Error
//
#if 0
extern boolean demorecording;
#endif

void I_Error (const char *error, ...)
{
    va_list     argptr;

    // Message first.
    va_start (argptr,error);
    fprintf (stderr, "Error: ");
    vfprintf (stderr,error,argptr);
    fprintf (stderr, "\n");
    va_end (argptr);

    fflush( stderr );

    D_Quit_Save( QUIT_panic );  // No save, safe shutdown

#ifdef LOGMESSAGES
    shutdown_logmessage( "I_Error()", "shutdown" );
#endif
   
    exit(-1);
}

#define MAX_QUIT_FUNCS     16
typedef void (*quitfuncptr)(void);
static quitfuncptr quit_funcs[MAX_QUIT_FUNCS] =
               { NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                 NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
               };
//
//  Adds a function to the list that need to be called by I_SystemShutdown().
//
void I_AddExitFunc(void (*func)(void))
{
   int c;

   for (c=0; c<MAX_QUIT_FUNCS; c++) {
      if (!quit_funcs[c]) {
         quit_funcs[c] = func;
         break;
      }
   }
}


#if 0
// Unused
//
//  Removes a function from the list that need to be called by
//   I_SystemShutdown().
//
void I_RemoveExitFunc(void (*func)(void))
{
   int c;

   for (c=0; c<MAX_QUIT_FUNCS; c++) {
      if (quit_funcs[c] == func) {
         while (c<MAX_QUIT_FUNCS-1) {
            quit_funcs[c] = quit_funcs[c+1];
            c++;
         }
         quit_funcs[MAX_QUIT_FUNCS-1] = NULL;
         break;
      }
   }
}
#endif

// Shutdown joystick and other interfaces, before I_ShutdownGraphics.
void I_Shutdown_IO(void)
{
    I_ShutdownJoystick();
}

//
//  Closes down everything. This includes restoring the initial
//  pallete and video mode, and removing whatever mouse, keyboard, and
//  timer routines have been installed.
//
//  NOTE : Shutdown user funcs. are effectively called in reverse order.
//
void I_ShutdownSystem(void)
{
   int c;

   for (c=MAX_QUIT_FUNCS-1; c>=0; c--)
      if (quit_funcs[c])
         (*quit_funcs[c])();

}

uint64_t I_GetDiskFreeSpace(void)
{
#ifdef LINUX
# ifdef SOLARIS
  goto guess;

# elif defined( __MACH__ ) || defined( NETBSD )
  struct statvfs stfs;
  if (statvfs(".", &stfs) == -1)
    goto guess;

  return (uint64_t) (stfs.f_bavail * stfs.f_bsize);
# else
  struct statfs stfs;
  if (statfs(".", &stfs) == -1)
    goto guess;

  return (uint64_t) (stfs.f_bavail * stfs.f_bsize);
# endif

#elif defined(WIN32)
  ULARGE_INTEGER free;
  if (!GetDiskFreeSpaceEx(NULL, &free, NULL, NULL))
    goto guess;

  return ((uint64_t)free.HighPart << 32) + free.LowPart;

#else
  // unknown
  goto guess;
#endif

guess:
  return INT_MAX;
}


char *I_GetUserName(void)
{
  static char username[MAXPLAYERNAME];
  char  *p;

#ifdef WIN32
  DWORD i = MAXPLAYERNAME;
  int ret = GetUserName(username, &i);
  if(!ret)
  {
#endif

  if ((p = getenv("USER")) == NULL)
    if ((p = getenv("user")) == NULL)
      if ((p = getenv("USERNAME")) == NULL)
        if ((p = getenv("username")) == NULL)
          return NULL;

  dl_strncpy(username, p, MAXPLAYERNAME);

#ifdef WIN32
  }
#endif

  if (strcmp(username, "") == 0)
    return NULL;

  return username;
}


// Get the directory of this program.
//   defdir: the current directory
//   dirbuf: a buffer of length MAX_WADPATH, 
// Return true when success, dirbuf contains the directory.
boolean I_Get_Prog_Dir( char * defdir, /*OUT*/ char * dirbuf )
{
    char * dnp;

#ifdef LINUX
# ifdef FREEBSD
#  define PROC_EXEC    "/proc/curproc/file"
# elif defined( NETBSD )
#  define PROC_EXEC    "/proc/curproc/exe"
# elif defined( SOLARIS )
#  define PROC_EXEC    "/proc/self/path/a.out"
# else
   // Linux
#  define PROC_EXEC    "/proc/self/exe"
# endif
#endif

#if defined(__APPLE__) && defined( __MACH__ )
   // derived from BSD, but DOES NOT have /proc
#endif

#ifdef PROC_EXEC
    // Get the executable path from /proc
    int len = readlink( PROC_EXEC, dirbuf, MAX_WADPATH-1 );
    if( len > 1 )
    {
        dirbuf[len] = 0;  // readlink does not terminate string
        goto got_path;
    }
#endif
   
#ifdef SOLARIS
    // [WDJ] Solaris, SunOS 5.10, get pathname of executable.
    // stdlib
    // Returns 0 when fails.
    const char *  execpath = getexecname();
    if( execpath )
    {
        // If not an absolute path (does not start with '/'), then can append it to result of getcwd().
        // defdir is from getcwd()
        if( (execpath[0] == '/')  // is absolute path already
            || (defdir == NULL) )   // defdir missing
        {
            // Prepend nothing
            defdir = "";
        }
        cat_filename( dirbuf, defdir, execpath );
        goto got_path;
    }
#endif

#if defined(__APPLE__) && defined( __MACH__ )
    uint32_t  bufsize = MAX_WADPATH-1;
    // [WDJ] Get a path to the executable.
    // Return -1 if buffer is not large enough, 0 if successful.
    if( _NSGetExecutablePath( dirbuf, & bufsize ) == 0 )
        goto got_path;
#endif

#ifdef WIN32
//    if(  )
    {
        // MS-Docs say Windows XP, but MinGW does not guard it.
        int len = GetModuleFileName( NULL, dirbuf, MAX_WADPATH-1 );
        if( len > 1 )
        {
            dirbuf[len] = 0;  // does not terminate string ??
            goto got_path;
        }
    }
#endif

    // The argv[0] method
    char * arg0p = myargv[0];
//    GenPrintf(EMSG_debug, "argv[0]=%s\n", arg0p );
#ifdef LINUX
    // Linux, FreeBSD, Mac
    if( arg0p[0] == '/' )
#else
    // Windows, DOS, OS2
    if( arg0p[0] == '\\' )
#endif
    {
        // argv[0] is an absolute path
        strncpy( dirbuf, arg0p, MAX_WADPATH-1 );
        dirbuf[MAX_WADPATH-1] = 0;
        goto got_path;
    }
#ifdef LINUX
    // Linux, FreeBSD, Mac
    else if( strchr( arg0p, '/' ) )
#else
    // Windows, DOS, OS2
    else if( strchr( arg0p, '/' ) || strchr( arg0p, '\\' ) )
#endif
    {
        // argv[0] is relative to current dir
        if( defdir )
        {
            cat_filename( dirbuf, defdir, arg0p );
            goto got_path;
        }
    }
    goto failed;
   
got_path:
    // Get only the directory name
    dnp = dirname( dirbuf );
    if( dnp == NULL )  goto failed;
    if( dnp != dirbuf )
    {
        cat_filename( dirbuf, "", dnp );
    }
    return true;

failed:
    dirbuf[0] = 0;
    return false;
}



int  I_mkdir(const char * new_dirname, int unixright)
{
//[segabor]  ([WDJ] from 143beta_macosx)
#if defined(LINUX) || defined(__MACH__)
    return mkdir(new_dirname, unixright);
#else
    return mkdir(new_dirname);
#endif
}



// return free and total system memory in bytes 
uint64_t I_GetFreeMem(uint64_t *total)
{
#ifdef LINUX
  // LINUX covers all the unix-type OS's.

#ifdef FREEBSD
    unsigned page_count, free_count, pagesize;
    size_t len = sizeof(unsigned);
    if (sysctlbyname("vm.stats.vm.v_page_count", &page_count, &len, NULL, 0))
      goto guess;
    if (sysctlbyname("vm.stats.vm.v_free_count", &free_count, &len, NULL, 0))
      goto guess;
    if (sysctlbyname("hw.pagesize", &pagesize, &len, NULL, 0))
      goto guess;
    *total = (uint64_t)page_count * pagesize;
    return (uint64_t)free_count * pagesize;
#elif defined(SOLARIS)
    goto guess;
#else
    // Actual Linux

#define MEMINFO_FILE "/proc/meminfo"
#define MEMTOTAL "MemTotal:"
#define MEMFREE "MemFree:"

    char buf[1024];    
    char *memTag;
    uint64_t freeKBytes;
    uint64_t totalKBytes;

    int meminfo_fd = open(MEMINFO_FILE, O_RDONLY);
    int n = read(meminfo_fd, buf, 1023);
    close(meminfo_fd);
    
    if(n<0)
      goto guess;
    
    buf[n] = '\0';
    if(NULL == (memTag = strstr(buf, MEMTOTAL)))
      goto guess;
        
    memTag += sizeof(MEMTOTAL);
    totalKBytes = atoi(memTag);
    
    if(NULL == (memTag = strstr(buf, MEMFREE)))
      goto guess;
        
    memTag += sizeof(MEMFREE);
    freeKBytes = atoi(memTag);
    
    *total = totalKBytes << 10;
    return freeKBytes << 10;
#endif

 guess:
    // make a conservative guess
    *total = (32 << 20) + 0x01;  // guess indicator
    return   0;
#elif defined(WIN32)
  // windows
#if defined(WIN_LARGE_MEM) && defined( _WIN32_WINNT ) && (_WIN32_WINNT >= 0x0500)
  // large memory status, only in newer libraries
  MEMORYSTATUSEX statex;
  statex.dwLength = sizeof(statex);
  GlobalMemoryStatusEx(&statex);
  *total = statex.ullTotalPhys;
  return statex.ullAvailPhys;
#else
  // older memory status
  MEMORYSTATUS statex;
  statex.dwLength = sizeof(statex);
  GlobalMemoryStatus(&statex);
  *total = statex.dwTotalPhys;
  return statex.dwAvailPhys;
#endif

#else
  // unknown
  // make a conservative guess
  *total = (32 << 20) + 0x01;  // guess indicator
  return   0;
#endif

}


#ifdef LOADING_DISK_ICON
//  Fab: this is probably to activate the 'loading' disc icon
//       it should set a flag, that I_FinishUpdate uses to know
//       whether it draws a small 'loading' disc icon on the screen or not
//
//  also it should explicitly draw the disc because the screen is
//  possibly not refreshed while loading
//
void I_BeginRead (void)
{
}

//  Fab: see above, end the 'loading' disc icon, set the flag false
//
void I_EndRead (void)
{
}
#endif
