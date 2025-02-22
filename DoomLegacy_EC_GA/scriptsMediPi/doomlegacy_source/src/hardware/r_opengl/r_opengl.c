// Emacs style mode select   -*- C++ -*-
//-----------------------------------------------------------------------------
//
// $Id: r_opengl.c 1593 2021-10-16 07:36:40Z wesleyjohnson $
//
// Copyright (C) 1998-2012 by DooM Legacy Team.
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
// $Log: r_opengl.c,v $
// Revision 1.60  2002/09/21 11:10:28  hurdler
//
// Revision 1.59  2002/06/30 21:37:48  hurdler
// Ready for 1.32 beta 5 release
//
// Revision 1.58  2002/01/05 16:39:19  hurdler
//
// Revision 1.57  2001/12/31 13:47:46  hurdler
// Add setcorona FS command and prepare the code for beta 4
//
// Revision 1.56  2001/12/27 22:50:26  hurdler
// fix a colormap bug, add scrolling floor/ceiling in hw mode
//
// Revision 1.55  2001/12/15 18:41:36  hurdler
// small commit, mainly splitscreen fix
//
// Revision 1.54  2001/08/27 19:59:35  hurdler
// Fix colormap in heretic + opengl, fixedcolormap and NEWCORONA
//
// Revision 1.53  2001/08/26 15:27:30  bpereira
// added fov for glide and fixed newcoronas code
//
// Revision 1.52  2001/08/19 15:40:07  bpereira
// added Treansform (and lighting) to glide
//
// Revision 1.51  2001/08/09 21:35:23  hurdler
// Add translucent 3D water in hw mode
//
// Revision 1.50  2001/08/08 20:34:44  hurdler
// Big TANDL update
//
// Revision 1.49  2001/08/07 00:44:06  hurdler
// MD2 implementation is getting better but still need lots of work
//
// Revision 1.48  2001/05/03 21:54:15  hurdler
// fix bis
//
// Revision 1.47  2001/05/03 20:05:57  hurdler
// small opengl fix
//
// Revision 1.46  2001/04/28 17:03:05  hurdler
// small fix for debug version and OS!=win32
//
// Revision 1.45  2001/04/28 15:19:32  hurdler
// fix PF_Occlude/PF_NoDepthTest
//
// Revision 1.44  2001/03/09 21:53:56  metzgermeister
// Revision 1.43  2001/02/28 17:50:56  bpereira
// Revision 1.42  2001/02/24 13:35:22  bpereira
//
// Revision 1.41  2001/02/19 17:45:20  hurdler
// Fix the problem of fullbright with Matrox's drivers under Linux
//
// Revision 1.40  2001/02/10 13:26:06  hurdler
// Revision 1.39  2001/01/25 18:56:28  bpereira
//
// Revision 1.38  2001/01/05 18:19:29  hurdler
// add renderer version checking
//
// Revision 1.37  2000/11/27 17:22:07  hurdler
// fix a small bug with GeForce based cards
//
// Revision 1.36  2000/11/02 19:49:39  bpereira
// Revision 1.35  2000/10/22 14:17:17  hurdler
//
// Revision 1.34  2000/10/04 16:27:56  hurdler
// Implement hardware texture memory stats
//
// Revision 1.33  2000/10/01 01:00:29  hurdler
// Fix a bug with PF_Invisible
//
// Revision 1.32  2000/09/28 20:57:21  bpereira
// Revision 1.31  2000/09/10 10:48:56  metzgermeister
// Revision 1.30  2000/08/10 19:58:04  bpereira
//
// Revision 1.29  2000/08/10 14:19:19  hurdler
// add waitvbl, fix sky problem
//
// Revision 1.28  2000/07/01 09:23:50  bpereira
//
// Revision 1.27  2000/06/08 19:41:53  hurdler
// my changes before splitting (can be reverted in development branch)
//
// Revision 1.26  2000/05/10 17:43:48  kegetys
// Sprites are drawn using PF_Environment
//
// Revision 1.25  2000/05/09 20:53:27  hurdler
// definitively fix the colormap
//
// Revision 1.24  2000/05/05 18:00:06  bpereira
// Revision 1.23  2000/04/30 10:30:10  bpereira
//
// Revision 1.22  2000/04/28 00:09:22  hurdler
// Full support of coronas in splitscreen mode
//
// Revision 1.21  2000/04/27 23:42:30  hurdler
// Change coronas' code for MiniGL compatibility
//
// Revision 1.20  2000/04/27 17:52:32  hurdler
// colormap code in hardware mode is now the default
//
// Revision 1.19  2000/04/24 15:20:40  hurdler
// Support colormap for text
//
// Revision 1.18  2000/04/23 15:07:37  hurdler
//
// Revision 1.17  2000/04/23 12:55:24  hurdler
// support filter mode in OpenGL
//
// Revision 1.16  2000/04/22 16:48:56  hurdler
//
// Revision 1.15  2000/04/22 16:48:00  hurdler
// support skin color
//
// Revision 1.14  2000/04/19 10:54:43  hurdler
//
// Revision 1.13  2000/04/18 16:07:47  hurdler
// better support of decals
//
// Revision 1.12  2000/04/18 14:49:25  hurdler
// fix a bug for Mesa 3.1 and previous
//
// Revision 1.11  2000/04/18 12:45:09  hurdler
// change a little coronas' code
//
// Revision 1.10  2000/04/16 18:38:07  bpereira
//
// Revision 1.9  2000/04/14 23:31:02  hurdler
// fix the bug of near clipping plane at startup
//
// Revision 1.8  2000/04/14 16:37:12  hurdler
// some nice changes for coronas
//
// Revision 1.7  2000/04/11 01:00:23  hurdler
// Better coronas support
//
// Revision 1.6  2000/04/09 17:18:24  hurdler
// modified coronas' code for 16 bits video mode
//
// Revision 1.5  2000/04/06 20:51:57  hurdler
// add support for new coronas
//
// Revision 1.4  2000/03/29 19:39:49  bpereira
//
// Revision 1.3  2000/03/07 03:31:14  hurdler
// fix linux compilation
//
// Revision 1.2  2000/02/27 00:42:11  hurdler
// Revision 1.1.1.1  2000/02/22 20:32:33  hurdler
// Initial import into CVS (v1.29 pr3)
//
//
// DESCRIPTION:
//      OpenGL API for Doom Legacy
//
//-----------------------------------------------------------------------------


#include <stdarg.h>
#include <math.h>

#include "doomincl.h"
#include "r_opengl.h"
#include "hardware/hw_glob.h"

// ==========================================================================
//                                                                  CONSTANTS
// ==========================================================================

// PI/2
#define N_PI_DEMI  (1.5707963268f)

// (320.0f/200.0f)
#define ASPECT_RATIO            (1.0f)
#define FAR_CLIPPING_PLANE      9000.0f
float   near_clipping_plane =   NEAR_CLIP_DIST;

#define MIPMAP_MASK     0x0100

// **************************************************************************
//                                                                    GLOBALS
// **************************************************************************

static char rendererString[256] = "Not Probed Yet";

// With OpenGL 1.1+, the first texture should be 1
// [WDJ] glGenTexture identifies the first texture available, it changes

static  GLuint      next_texture_id = 0;
static  GLuint      no_texture_id   = 0;  // small white texture
static  GLuint      tex_downloaded  = 0;
static  GLfloat     fov             = 90.0;
static  GLuint      tint_color_id   = 0;  // Imitate the special object palette tints
static  RGBA_float_t  tint_rgb;
static  FBITFIELD   cur_polyflags;

static  FTextureInfo_t*  gr_cachetail = NULL;
static  FTextureInfo_t*  gr_cachehead = NULL;

RGBA_t  myPaletteData[256];
GLint   screen_width;               // used by Draw2DLine()
GLint   screen_height;
GLbyte  screen_depth;
GLint   textureformatGL;

GLint min_filter = GL_LINEAR;
GLint mag_filter = GL_LINEAR;

static const RGBA_t  RGBA_zero = {0}; // union uint32_t

const   GLubyte     *gl_extensions;
int     oglflags = 0;

//Hurdler: 04/10/2000: added for the kick ass coronas as Boris wanted ;-)
#ifndef MINI_GL_COMPATIBILITY
static GLdouble    modelMatrix[16];
static GLdouble    projMatrix[16];
static GLint       viewport[4]; 
#endif


#ifdef USE_PALETTED_TEXTURE
    PFNGLCOLORTABLEEXTPROC  glColorTableEXT;
    GLboolean               usePalettedTexture;
    GLubyte                 palette_tex[768];
#endif

// shortcut for ((float)1/i)

// Transform to glcolor space.   (i / 255.0f)
static const GLfloat    to_glcolor_float[256] = {
    0.000000f, 0.003922f, 0.007843f, 0.011765f, 0.015686f, 0.019608f, 0.023529f, 0.027451f,
    0.031373f, 0.035294f, 0.039216f, 0.043137f, 0.047059f, 0.050980f, 0.054902f, 0.058824f,
    0.062745f, 0.066667f, 0.070588f, 0.074510f, 0.078431f, 0.082353f, 0.086275f, 0.090196f,
    0.094118f, 0.098039f, 0.101961f, 0.105882f, 0.109804f, 0.113725f, 0.117647f, 0.121569f,
    0.125490f, 0.129412f, 0.133333f, 0.137255f, 0.141176f, 0.145098f, 0.149020f, 0.152941f,
    0.156863f, 0.160784f, 0.164706f, 0.168627f, 0.172549f, 0.176471f, 0.180392f, 0.184314f,
    0.188235f, 0.192157f, 0.196078f, 0.200000f, 0.203922f, 0.207843f, 0.211765f, 0.215686f,
    0.219608f, 0.223529f, 0.227451f, 0.231373f, 0.235294f, 0.239216f, 0.243137f, 0.247059f,
    0.250980f, 0.254902f, 0.258824f, 0.262745f, 0.266667f, 0.270588f, 0.274510f, 0.278431f,
    0.282353f, 0.286275f, 0.290196f, 0.294118f, 0.298039f, 0.301961f, 0.305882f, 0.309804f,
    0.313726f, 0.317647f, 0.321569f, 0.325490f, 0.329412f, 0.333333f, 0.337255f, 0.341176f,
    0.345098f, 0.349020f, 0.352941f, 0.356863f, 0.360784f, 0.364706f, 0.368627f, 0.372549f,
    0.376471f, 0.380392f, 0.384314f, 0.388235f, 0.392157f, 0.396078f, 0.400000f, 0.403922f,
    0.407843f, 0.411765f, 0.415686f, 0.419608f, 0.423529f, 0.427451f, 0.431373f, 0.435294f,
    0.439216f, 0.443137f, 0.447059f, 0.450980f, 0.454902f, 0.458824f, 0.462745f, 0.466667f,
    0.470588f, 0.474510f, 0.478431f, 0.482353f, 0.486275f, 0.490196f, 0.494118f, 0.498039f,
    0.501961f, 0.505882f, 0.509804f, 0.513726f, 0.517647f, 0.521569f, 0.525490f, 0.529412f,
    0.533333f, 0.537255f, 0.541177f, 0.545098f, 0.549020f, 0.552941f, 0.556863f, 0.560784f,
    0.564706f, 0.568627f, 0.572549f, 0.576471f, 0.580392f, 0.584314f, 0.588235f, 0.592157f,
    0.596078f, 0.600000f, 0.603922f, 0.607843f, 0.611765f, 0.615686f, 0.619608f, 0.623529f,
    0.627451f, 0.631373f, 0.635294f, 0.639216f, 0.643137f, 0.647059f, 0.650980f, 0.654902f,
    0.658824f, 0.662745f, 0.666667f, 0.670588f, 0.674510f, 0.678431f, 0.682353f, 0.686275f,
    0.690196f, 0.694118f, 0.698039f, 0.701961f, 0.705882f, 0.709804f, 0.713726f, 0.717647f,
    0.721569f, 0.725490f, 0.729412f, 0.733333f, 0.737255f, 0.741177f, 0.745098f, 0.749020f,
    0.752941f, 0.756863f, 0.760784f, 0.764706f, 0.768627f, 0.772549f, 0.776471f, 0.780392f,
    0.784314f, 0.788235f, 0.792157f, 0.796078f, 0.800000f, 0.803922f, 0.807843f, 0.811765f,
    0.815686f, 0.819608f, 0.823529f, 0.827451f, 0.831373f, 0.835294f, 0.839216f, 0.843137f,
    0.847059f, 0.850980f, 0.854902f, 0.858824f, 0.862745f, 0.866667f, 0.870588f, 0.874510f,
    0.878431f, 0.882353f, 0.886275f, 0.890196f, 0.894118f, 0.898039f, 0.901961f, 0.905882f,
    0.909804f, 0.913726f, 0.917647f, 0.921569f, 0.925490f, 0.929412f, 0.933333f, 0.937255f,
    0.941177f, 0.945098f, 0.949020f, 0.952941f, 0.956863f, 0.960784f, 0.964706f, 0.968628f,
    0.972549f, 0.976471f, 0.980392f, 0.984314f, 0.988235f, 0.992157f, 0.996078f, 1.000000
};


static I_Error_t I_Error_GL = NULL;
//static byte gl_verbose = 0;
#ifdef DEBUG_TO_FILE
static FILE * ogl_log = NULL;
static boolean log_enable = true;
#endif

void DBG_close( void )
{
#ifdef DEBUG_TO_FILE
    if(ogl_log) fclose(ogl_log);
#endif
}


// -----------------+
// DBG_Printf       : Output error messages to debug log if DEBUG_TO_FILE is defined,
//                  : else do nothing
// Returns          :
// -----------------+
void DBG_Printf( LPCTSTR lpFmt, ... )
{
    va_list ap;

#define DBG_BUF_SIZE 4096
#if (LOGLINELEN + 32) > DBG_BUF_SIZE
#undef DBG_BUF_SIZE  
#define DBG_BUF_SIZE  (LOGLINELEN*2 + 32)
#endif

#ifdef DEBUG_TO_FILE
    char    dbgbuf[DBG_BUF_SIZE];

    va_start(ap, lpFmt);
    vsnprintf(dbgbuf, DBG_BUF_SIZE, lpFmt, ap);
    dbgbuf[DBG_BUF_SIZE-1] = '\0'; // term, when length limited
    va_end(ap);

    // [WDJ] As a library routine, cannot access var or func of calling program.
    // So this uses separate file handling.
    // Accesses of logstream or verbose will compile but it prevents the
    // lib from loading at dlopen.
    if( log_enable && ! ogl_log )
    {
        // open on first usage
        printf( "Open log: %s\n", DEBUG_TO_FILE );
        ogl_log = fopen( DEBUG_TO_FILE, "w" );
        log_enable = false;
    }
    if( ogl_log )
    {
        fputs(dbgbuf, ogl_log);
    }
#endif

//    if(gl_verbose > 1)
    {
      va_start(ap, lpFmt);
      vprintf( lpFmt, ap );
      va_end(ap);
    }
}

// [WDJ] Print a long string as multiple lines of LOGLINELEN
// To Fix overrun of DBG_Printf buffer by long GL_EXTENSION string
void  DBG_Print_lines( const char * longstr )
{
    char lbf[ LOGLINELEN+2 ];
    while( longstr )
    {
        lbf[LOGLINELEN+1] = 0; // safety
        lbf[LOGLINELEN] = 0;  // detect
        strncpy( lbf, longstr, LOGLINELEN );  // get some or all
        if( lbf[LOGLINELEN] )  // too long, partial copy
        {
            lbf[LOGLINELEN] = 0;
            char * lsp = strrchr( lbf, ' ' );  // find last space
            if( lsp == NULL )
                lsp = & lbf[LOGLINELEN];  // should not happen
            *lsp = '\0';  // term string at space
            longstr += ( lsp - lbf + 1 );
        }
        else
        {
            longstr = NULL;  // end
        }
        DBG_Printf("  %s\n", lbf);
    }
}

static byte enable_card_display = 1;

// [WDJ] Query the GL hardware strings
// set oglflags and gl_extensions
// Do not call before initializing GL
void VIDGL_Query_GL_info( int ogltest )
{
    if( enable_card_display )
       DBG_Printf("Vendor     : %s\n", glGetString(GL_VENDOR) );
//#define DUP_RENDERER_STR
#ifdef DUP_RENDERER_STR
    // unnecessary dup
    char * renderer = strdup( (char*) glGetString(GL_RENDERER));
#else
    const char * renderer = (char*) glGetString(GL_RENDERER);
#endif
    if( enable_card_display )
       DBG_Printf("Renderer   : %s\n", renderer );
    // BP: disable advanced features that don't work on some hardware
    if( strstr(renderer, "810" ) )   oglflags |= GLF_NOZBUFREAD;
    // Win: Hurdler: Now works on G400 with bios 1.6 and certified drivers 6.04
    // X11: Hurdler: now yes (due to that fullbright bug with g200/g400 card)
    if( strstr(renderer, "G200" ) )  oglflags |= GLF_NOTEXENV;
    if( strstr(renderer, "G400" ) )  oglflags |= GLF_NOTEXENV;
    oglflags &= ogltest;  // port specific
#ifdef DUP_RENDERER_STR
    free(renderer);
#endif
    gl_extensions = glGetString(GL_EXTENSIONS);  // passed to VIDGL_isExtAvailable

    if( enable_card_display )
    {
        DBG_Printf("Version    : %s\n", glGetString(GL_VERSION) );
        // [WDJ] Extensions string is indefinite long
        DBG_Printf("Extensions : \n" );
        DBG_Print_lines( (char*)gl_extensions );

        DBG_Printf("oglflags   : 0x%X\n", oglflags );
        enable_card_display = 0;  // only once
    }
}


// [WDJ] Linux seems to work even without the White_texture, but Win32 fails
// with any variation from the example procedures.
#ifndef LINUX
#define LITTLE_WHITE_TEXTURE
#endif

#ifdef LITTLE_WHITE_TEXTURE
// Bind little white RGBA texture to ID no_texture_id.
static FUINT  White_texture[8*8];
#endif

// -----------------+
// SetNoTexture     : Disable texture
// -----------------+
static void SetNoTexture( void )
{
    // Set small white texture.
    if( tex_downloaded != no_texture_id )
    {
        // SetNoTexture is invoked by GenPrint, so cannot use GenPrint here.
//        fprintf( stderr, "Set NoTexture\n" );
        tex_downloaded = no_texture_id;
        glBindTexture( GL_TEXTURE_2D, no_texture_id );
    }
}


// -----------------+
// VIDGL_Set_GL_Model_View  :
// -----------------+
// Called by ogl_sdl:OglSdlSurface or ogl_mac:OglMacSurface
void VIDGL_Set_GL_Model_View( GLint w, GLint h )
{
    DBG_Printf( "VIDGL_Set_GL_Model_View(): %dx%d\n", w, h );

    screen_width = w;
    screen_height = h;

#ifdef MAC_SDL
    // SDL tutorial for Mac does not call glViewport, use default
#else
    glViewport( 0, 0, w, h );
#endif

    glMatrixMode( GL_PROJECTION );
    glLoadIdentity();
    gluPerspective( fov, ASPECT_RATIO, near_clipping_plane, FAR_CLIPPING_PLANE);

    glMatrixMode( GL_MODELVIEW );
    glLoadIdentity();
    //glScalef(1.0f, 320.0f/200.0f, 1.0f);  // gr_scalefrustum (ORIGINAL_ASPECT)

    // added for new coronas' code (without depth buffer)
#ifndef MINI_GL_COMPATIBILITY
    glGetIntegerv(GL_VIEWPORT, viewport); 
    glGetDoublev(GL_PROJECTION_MATRIX, projMatrix);
#endif
}


// -----------------+
// VIDGL_Set_GL_States : Set permanent states
// -----------------+
// Called by ogl_sdl:OglSdlSurface or ogl_mac:OglMacSurface
// Called after VIDGL_Set_GL_Model_View
void VIDGL_Set_GL_States( void )
{
    DBG_Printf( "VIDGL_Set_GL_States()\n" );

    // Hurdler: not necessary, is it?
    //glShadeModel( GL_SMOOTH );      // iterate vertice colors
    glShadeModel( GL_FLAT );

    glEnable( GL_TEXTURE_2D );      // two-dimensional texturing
    glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE );

    glAlphaFunc( GL_NOTEQUAL, 0 );
    //glDisable( GL_ALPHA_TEST );     // enable alpha testing
    //glBlendFunc( GL_ONE, GL_ZERO ); // copy pixel to frame buffer (opaque)
    glEnable( GL_BLEND );           // enable color blending

    glColorMask( GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE );

//    glDisable(GL_DITHER);         // faB: ??? (undocumented in OpenGL 1.1)
                                  // Hurdler: yes, it is!
    glEnable( GL_DEPTH_TEST );    // check the depth buffer
    //glDepthMask( 1 );             // enable writing to depth buffer
    glClearDepth( 1.0 );
    glDepthRange( 0.0, 1.0 );
    glDepthFunc(GL_LEQUAL);

    // this set cur_polyflags to the actual configuration
    cur_polyflags = 0xffffffff;
    SetBlend(0);

#ifdef LITTLE_WHITE_TEXTURE
    // init White_texture
//    memset( White_texture, 0xFF, 8*8*sizeof(White_texture[0]));
    memset( White_texture, 0xFF, sizeof(White_texture));
#endif

    next_texture_id = 0;
    glGenTextures( 1, &next_texture_id );
    no_texture_id = next_texture_id ++;
#if 0   
//    if( gl_verbose>1 )
      fprintf( stderr, "VIDGL_Set_GL_States: no_texture_id = %i\n", no_texture_id );
#endif

#ifdef LITTLE_WHITE_TEXTURE
    // Direct
    tex_downloaded = no_texture_id;
    glBindTexture( GL_TEXTURE_2D, no_texture_id );
    glTexImage2D( GL_TEXTURE_2D, 0, 4, 8, 8, 0, GL_RGBA, GL_UNSIGNED_BYTE, White_texture );
//    fprintf( stderr, "VIDGL_Set_GL_States: White_texture set\n" );
#else
    tex_downloaded = -1;  // init to invalid
//    SetNoTexture();
#endif

    glPolygonOffset(-1.0, -1.0);

    //glEnable(GL_CULL_FACE);
    //glCullFace(GL_FRONT);
    //glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
    //glPolygonMode(GL_FRONT, GL_LINE);

    //glFogi(GL_FOG_MODE, GL_EXP);
    //glHint(GL_FOG_HINT, GL_NICEST);
    //glFogfv(GL_FOG_COLOR, fogcolor);
    //glFogf(GL_FOG_DENSITY, 0.0005);

    // bp : when no t&l :)
    glLoadIdentity();
    glScalef(1.0, 1.0f, -1.0f);
#ifndef MINI_GL_COMPATIBILITY
    glGetDoublev(GL_MODELVIEW_MATRIX, modelMatrix); // added for new coronas' code (without depth buffer)
#endif
}


// -----------------+
// VIDGL_Flush_GL_textures : flush OpenGL textures
//                   : Clear list of downloaded mipmaps
// -----------------+
void VIDGL_Flush_GL_textures( void )
{
    //DBG_Printf ("VIDGL_Flush_GL_textures()\n");

    while( gr_cachehead )
    {
        // ceci n'est pas du tout necessaire vu que tu les a charger normalement et
        // donc il sont dans ta liste !
#if 0
        //Hurdler: 25/04/2000: now support colormap in hardware mode
        FTextureInfo_t    *tmp = gr_cachehead->nextskin;

        // The memory should be freed in the main code
        while (tmp)
        {
            glDeleteTextures( 1, &tmp->downloaded );
            tmp->downloaded = 0;
            tmp = tmp->nextcolormap;
        }
#endif
        glDeleteTextures( 1, &gr_cachehead->downloaded );
        gr_cachehead->downloaded = 0;
        gr_cachehead = gr_cachehead->nextmipmap;
    }
    gr_cachetail = gr_cachehead = NULL; //Hurdler: well, gr_cachehead is already NULL
#if 1
    next_texture_id = no_texture_id + 1; // reset texture id usage
#else
    glGenTextures( 1, &next_texture_id );  // restart texture id usage
    // no_texture_id might move
    no_texture_id = next_texture_id++;
    glBindTexture( GL_TEXTURE_2D, no_texture_id );
    glTexImage2D( GL_TEXTURE_2D, 0, 4, 8, 8, 0, GL_RGBA, GL_UNSIGNED_BYTE, White_texture );
#endif
    tex_downloaded = 0;
}


// -----------------+
// VIDGL_isExtAvailable : Look if an OpenGL extension is available
// Returns          : true if extension available
// -----------------+
int VIDGL_isExtAvailable(char *extension)
{
    const GLubyte   *start;
    GLubyte         *where, *terminator;

    where = (GLubyte *) strchr(extension, ' ');
    if (where || *extension == '\0')
        return 0;

    start = gl_extensions;
    for (;;)
    {
        where = (GLubyte *) strstr((const char *) start, extension);
        if (!where)
            break;

        terminator = where + strlen(extension);
        if (where == start || *(where - 1) == ' ')
        {
            if (*terminator == ' ' || *terminator == '\0')
                return 1;
        }
        start = terminator;
    }
    return 0;
}


// -----------------+
// Init             : Initialise the OpenGL interface API
// Returns          :
// -----------------+
EXPORT boolean HWRAPI( Init ) (I_Error_t FatalErrorFunction)
{
    // param needed
    // gl_verbose = verbose;
    // VERSION_BANNER
    // VERSION        
    I_Error_GL = FatalErrorFunction;
//    DBG_Printf ("%s, %s\n", DRIVER_STRING, VERSION_BANNER);
    DBG_Printf ("%s\n", DRIVER_STRING);
    return 1;
}


// -----------------+
// ClearMipMapCache : Flush OpenGL textures from memory
// -----------------+
EXPORT void HWRAPI( ClearMipMapCache ) ( void )
{
    // DBG_Printf ("HWR_Flush(exe)\n");
    VIDGL_Flush_GL_textures();
}


// -----------------+
// ReadRect         : Read a rectangle region of the truecolor framebuffer.
// Returns          : Return 24 bit RGB, set bitpp to 24.
// -----------------+
EXPORT void HWRAPI( ReadRect ) (int x, int y, int width, int height,
                                /*OUT*/ byte * buf, byte * bitpp )
{
    // DBG_Printf ("ReadRect()\n");
    GLubyte *image;
    int i, j;

    image = (GLubyte *) malloc(width*height*3*sizeof(GLubyte));
    glReadPixels(x, y, width, height, GL_RGB, GL_UNSIGNED_BYTE, image);

    // Flip vertically, reverse RGB.
    byte * bp = & buf[0];
    for (i=height-1; i>=0; i--)
    {
        GLubyte * pix = & image[ i * width * 3 ];
        for (j=0; j<width; j++)
        {
            *(bp++) = pix[2];  // R
            *(bp++) = pix[1];  // G
            *(bp++) = pix[0];  // B
            pix += 3;
        }
    }

    free(image);
    *bitpp = 24;  // return output
}


// -----------------+
// GClipRect        : Defines the 2D hardware clipping window
// -----------------+
EXPORT void HWRAPI( GClipRect ) (int minx, int miny, int maxx, int maxy, float nearclip)
{
    // DBG_Printf ("GClipRect(%d, %d, %d, %d)\n", minx, miny, maxx, maxy);

    glViewport( minx, screen_height-maxy, maxx-minx, maxy-miny );
    near_clipping_plane = nearclip;

    //glScissor(minx, screen_height-maxy, maxx-minx, maxy-miny);
    glMatrixMode( GL_PROJECTION );
    glLoadIdentity();
    gluPerspective( fov, ASPECT_RATIO, near_clipping_plane, FAR_CLIPPING_PLANE);
    glMatrixMode(GL_MODELVIEW);

    // added for new coronas' code (without depth buffer)
#ifndef MINI_GL_COMPATIBILITY
    glGetIntegerv(GL_VIEWPORT, viewport);
    glGetDoublev(GL_PROJECTION_MATRIX, projMatrix);
#endif
}


// -----------------+
// ClearBuffer      : Clear the color/alpha/depth buffer(s)
// -----------------+
EXPORT void HWRAPI( ClearBuffer ) ( boolean ColorMask, boolean DepthMask,
                                    RGBA_float_t * ClearColor )
{
    // DBG_Printf ("ClearBuffer(%d)\n", alpha);
    FUINT   ClearMask = 0;
    FBITFIELD  polyflags = cur_polyflags & ~PF_Occlude;

    if( ColorMask )
    {
        if( ClearColor )
        {
            glClearColor( ClearColor->red, ClearColor->green,
                          ClearColor->blue, ClearColor->alpha );
        }
        ClearMask |= GL_COLOR_BUFFER_BIT;
    }
    if( DepthMask )
    {
        //glClearDepth( 1.0 );     //Hurdler: all that are permanen states
        //glDepthRange( 0.0, 1.0 );
        //glDepthFunc( GL_LEQUAL );
        ClearMask |= GL_DEPTH_BUFFER_BIT;
        polyflags |= PF_Occlude;
    }

    SetBlend( polyflags );

    glClear( ClearMask );
}


// -----------------+
// HWRAPI Draw2DLine: Render a 2D line
// -----------------+
EXPORT void HWRAPI( Draw2DLine ) ( v2d_t * v1, v2d_t * v2, RGBA_t Color )
{
    RGBA_float_t c;

    // DBG_Printf ("DrawLine() (%f %f %f) %d\n", v1->x, -v1->y, -v1->z, v1->argb);
#ifdef MINI_GL_COMPATIBILITY
    GLfloat x1, x2, x3, x4;
    GLfloat y1, y2, y3, y4;
    GLfloat dx, dy;
    GLfloat angle;
#endif

    // BP: we should reflect the new state in our variable
    //SetBlend( PF_Modulated|PF_NoTexture );

    glDisable( GL_TEXTURE_2D );

    c.red   = to_glcolor_float[Color.s.red];
    c.green = to_glcolor_float[Color.s.green];
    c.blue  = to_glcolor_float[Color.s.blue];
    c.alpha = to_glcolor_float[Color.s.alpha];

#ifndef MINI_GL_COMPATIBILITY
    glColor4fv( (float *)&c );    // is in RGBA float format
    glBegin(GL_LINES);
        glVertex3f(v1->x, -v1->y, 1);
        glVertex3f(v2->x, -v2->y, 1);
    glEnd();
#else
    angle = ( v2->x != v1->x )?
          (float)atan((v2->y - v1->y)/(v2->x - v1->x))
        : N_PI_DEMI;
    dx = (float)sin(angle) / (float)screen_width;
    dy = (float)cos(angle) / (float)screen_height;

    x1 = v1->x - dx;  y1 = v1->y + dy;
    x2 = v2->x - dx;  y2 = v2->y + dy;
    x3 = v2->x + dx;  y3 = v2->y - dy;
    x4 = v1->x + dx;  y4 = v1->y - dy;

    glColor4f(c.red, c.green, c.blue, c.alpha);
    glBegin( GL_TRIANGLE_FAN );
        glVertex3f( x1, -y1, 1 );
        glVertex3f( x2, -y2, 1 );
        glVertex3f( x3, -y3, 1 );
        glVertex3f( x4, -y4, 1 );
    glEnd();
#endif

    glEnable( GL_TEXTURE_2D );
}


#ifdef BLEND_FIELD
typedef struct  
{
    uint16_t sfac, dfac;
} gl_blend_param_t;

// The blend param for the PF_blend_field values.
gl_blend_param_t blend_param[8] =
{
  // { sfac, dfac }
  //   sfac = alpha to apply to source
  //   dfac = alpha to apply to existing dest
// none, Overwrite
  { GL_ONE, GL_ZERO },   // the same as no blending
// PF_Masked,       Poly is alpha scaled and 0 alpha pels are discarded (holes in texture)
  // Hurdler: does that mean lighting is only made by alpha src?
  // it sounds ok, but not for polygonsmooth
  { GL_SRC_ALPHA, GL_ZERO },                // 0 alpha = holes in texture
// PF_Translucent,  Poly is transparent, alpha = level of transparency
  { GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA }, // alpha = level of transparency
// PF_Additive,     Poly is added to the frame buffer
#ifdef ATI_RAGE_PRO_COMPATIBILITY
  { GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA }, // alpha = level of transparency
#else
  { GL_SRC_ALPHA, GL_ONE },                 // src * alpha + dest
#endif
// PF_Environment,  Poly should be drawn environment mapped (text drawing)
  { GL_ONE, GL_ONE_MINUS_SRC_ALPHA },       // 
// PF_Subtractive, for splat
  // good for shadow
  // not realy but what else ?
  { GL_ZERO, GL_ONE_MINUS_SRC_COLOR },      //
// PF_InvisibleB
  { GL_ZERO, GL_ONE },                      // Transparent
// Unused
  { GL_ZERO, GL_ONE },
};
#endif

// -----------------+
// SetBlend         : Set render mode
// -----------------+
// PF_Masked - we could use an ALPHA_TEST of GL_EQUAL, and alpha ref of 0,
//             is it faster when pixels are discarded ?
EXPORT void HWRAPI( SetBlend ) ( FBITFIELD polyflags )
{
    // SetBlend is invoked by GenPrint, so cannot use GenPrint here.
    // xf are the polyflags that changed.
    FBITFIELD  xf = cur_polyflags ^ polyflags;

#ifdef BLEND_FIELD
    if( xf &  (PF_blend_field | PF_NoAlphaTest) )
    {
        // PF_blend_field values: 0, PF_Environment, PF_Additive, PF_Translucent, PF_Masked, PF_Subtractive
        // Blend mode must be changed.
        gl_blend_param_t *  bp = & blend_param[ polyflags & PF_blend_field8 ];  // PF_Blend field, only 8 entries
        glBlendFunc( bp->sfac, bp->dfac );

        // This is highly correlated with PF_Additive.
        if( xf & PF_NoAlphaTest )
        {
            if( polyflags & PF_NoAlphaTest)
                glDisable( GL_ALPHA_TEST );
            else
                glEnable( GL_ALPHA_TEST );      // discard 0 alpha pixels (holes in texture)
        }
    }

    if( xf &  (PF_Occlude|PF_NoTexture|PF_Modulated|PF_NoDepthTest|PF_Decal) )
    {       
#else
    if( xf & ( PF_Blending|PF_Occlude|PF_NoTexture|PF_Modulated|PF_NoDepthTest|PF_Decal|PF_InvisibleColor|PF_NoAlphaTest ) )
    {
        // One of these flags has changed
        // PF_Blending = (PF_Environment|PF_Additive|PF_Translucent|PF_Masked|PF_Subtractive)
        if( xf & PF_Blending ) // if blending mode must be changed
        {
            // PF_Blending flags are mutually exclusive
            switch(polyflags & PF_Blending) {
                case PF_Translucent & PF_Blending:
                     glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA ); // alpha = level of transparency
                     break;
                case PF_Masked & PF_Blending:
                     // Hurdler: does that mean lighting is only made by alpha src?
                     // it sounds ok, but not for polygonsmooth
                     glBlendFunc( GL_SRC_ALPHA, GL_ZERO );                // 0 alpha = holes in texture
                     break;
                case PF_Additive & PF_Blending:
#ifdef ATI_RAGE_PRO_COMPATIBILITY
                     glBlendFunc( GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA ); // alpha = level of transparency
#else
                     glBlendFunc( GL_SRC_ALPHA, GL_ONE );                 // src * alpha + dest
#endif
                     break;
                case PF_Environment & PF_Blending:
                     glBlendFunc( GL_ONE, GL_ONE_MINUS_SRC_ALPHA );
                     break;
                case PF_Subtractive & PF_Blending:
                     // good for shadow
                     // not realy but what else ?
                     glBlendFunc( GL_ZERO, GL_ONE_MINUS_SRC_COLOR);
                     break;
                default : // must be 0, otherwise it's an error
                     // No blending
                     glBlendFunc( GL_ONE, GL_ZERO );   // the same as no blending
                     break;
            }
        }

        if( xf & PF_NoAlphaTest)
        {
            if( polyflags & PF_NoAlphaTest)
                glDisable( GL_ALPHA_TEST );
            else
                glEnable( GL_ALPHA_TEST );      // discard 0 alpha pixels (holes in texture)
        }
#endif

        if( xf & PF_Decal )
        {
            if( polyflags & PF_Decal )
                glEnable(GL_POLYGON_OFFSET_FILL);
            else
                glDisable(GL_POLYGON_OFFSET_FILL);
        }
        if( xf & PF_NoDepthTest )
        {
            if( polyflags & PF_NoDepthTest )
            {
                glDepthFunc(GL_ALWAYS); //glDisable( GL_DEPTH_TEST );
            }
            else
                glDepthFunc(GL_LEQUAL); //glEnable( GL_DEPTH_TEST );
        }
        if( xf & PF_Modulated )
        {
            if (oglflags & GLF_NOTEXENV)
            { // [smite] FIXME this was only for LINUX but why?
              // WIN32: if not present, menu shading draws only the corner (rest is black), and menu is grayed
                if ( !(polyflags & PF_Modulated) )
                    glColor4f(1.0f, 1.0f, 1.0f, 1.0f);
            }
            else
            if( polyflags & PF_Modulated )
            {   // mix texture colour with Surface->FlatColor
                glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE );
            }
            else
            {   // colour from texture is unchanged before blending
                glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE );
            }
        }
        if( xf & PF_Occlude ) // depth test but (no) depth write
        {
            if (polyflags&PF_Occlude)
            {
                glDepthMask( 1 );
            }
            else
                glDepthMask( 0 );
        }
#ifndef BLEND_FIELD
        if( xf & PF_InvisibleColor )
        {
#if 0
	    boolean nic = (polyflags & PF_InvisibleColor)==0;  // normally true
            glColorMask( nic, nic, nic, nic );
#endif
            
            if (polyflags & PF_InvisibleColor)
                glBlendFunc( GL_ZERO, GL_ONE );         // transparent blending
            else
            {   // big hack: (TODO: manage that better)
                // we test only for PF_Masked because PF_Invisible is only used 
                // (for now) with it (yeah, that's crappy, sorry)
                if ((polyflags & PF_Blending) == PF_Masked)
                    glBlendFunc( GL_SRC_ALPHA, GL_ZERO );  
            }
        }
#endif
        if( polyflags & PF_NoTexture )
        {
            SetNoTexture();
        }
    }
    cur_polyflags = polyflags;
}


// -----------------+
// SetTexture       : The mipmap becomes the current texture source
// -----------------+
EXPORT void HWRAPI( SetTexture ) ( FTextureInfo_t *pTexInfo )
{
    if( pTexInfo->downloaded )
    {
        if (pTexInfo->downloaded != tex_downloaded)
        {
            glBindTexture(GL_TEXTURE_2D, pTexInfo->downloaded);
            tex_downloaded = pTexInfo->downloaded;
        }
    }
    else
    {
        // Download a mipmap
        static RGBA_t   tex[256*256];
        RGBA_t          *ptex = tex;
        int             w, h;

        //DBG_Printf ("DownloadMipmap %d %x\n", next_texture_id, pTexInfo->GR_data);

        w = pTexInfo->width;
        h = pTexInfo->height;

#ifdef USE_PALETTED_TEXTURE
        if( usePalettedTexture
            && (pTexInfo->GR_format==GR_TEXFMT_P_8)
            && !(pTexInfo->flags & TF_CHROMAKEYED) )
        {
            // do nothing here.
            // Not a problem with MiniGL since we don't use paletted texture
        }
        else
#endif
        if( (pTexInfo->GR_format == GR_TEXFMT_P_8)
            || (pTexInfo->GR_format == GR_TEXFMT_AP_88) )
        {
            GLubyte *pImgData;
            int i, j;
            byte  src_inc = ( pTexInfo->GR_format == GR_TEXFMT_AP_88 )? 2 : 1;

            pImgData = (GLubyte *)pTexInfo->GR_data;
            if( pTexInfo->tfflags & TF_CHROMAKEYED )
            {
                // [WDJ] Chromakey
                // OpenGL does not use chromakey, it uses alpha.
                // [WDJ] Chromakey ignores alpha of source ?		       
                // [WDJ] Much faster to not test every pixel, make use of the lookup to subst chromakey.
                RGBA_t  myPaletteData_chromakey_save = myPaletteData[ HWR_PATCHES_CHROMAKEY_COLORINDEX ];
                myPaletteData[ HWR_PATCHES_CHROMAKEY_COLORINDEX ] = RGBA_zero;  // alpha = 0

                for( j=0; j<h; j++ )
                {
                    for( i=0; i<w; i++)
                    {
                        // [WDJ] dest and src are both RGBA_t
                        tex[w*j+i] = myPaletteData[*pImgData];
                        pImgData += src_inc;
                    }
                }
                // [WDJ] Restore palette	       
                myPaletteData[ HWR_PATCHES_CHROMAKEY_COLORINDEX ] = myPaletteData_chromakey_save;
            }
            else if( pTexInfo->GR_format == GR_TEXFMT_AP_88 )
            {
                // [WDJ] No Chromakey, color, alpha.
                for( j=0; j<h; j++ )
                {
                    for( i=0; i<w; i++)
                    {
                        register RGBA_t  t2 = myPaletteData[*pImgData++];
                        t2.s.alpha = *pImgData++;  // alpha
                        tex[w*j+i] = t2;
                    }
                }
            }
            else
            {
                // [WDJ] No Chromakey, color.
                for( j=0; j<h; j++ )
                {
                    for( i=0; i<w; i++)
                    {
                        tex[w*j+i] = myPaletteData[*pImgData];
                        pImgData++;
                    }
                }
            }
        }
        else if( pTexInfo->GR_format == GR_RGBA )
        {
            // corona test : passed as ARGB 8888, which is not in glide formats
            // Hurdler: not used for coronas anymore, just for dynamic lighting
            ptex = (RGBA_t *) pTexInfo->GR_data;
        }
        else if( pTexInfo->GR_format == GR_TEXFMT_ALPHA_INTENSITY_88 )
        {
            GLubyte *pImgData;
            int i, j;

            pImgData = (GLubyte *)pTexInfo->GR_data;
            for( j=0; j<h; j++ )
            {
                for( i=0; i<w; i++)
                {
                    register RGBA_t  t2;
                    // mono
                    t2.s.red = t2.s.green = t2.s.blue = *pImgData;
                    pImgData++;
                    t2.s.alpha = *pImgData;
                    pImgData++;
                    tex[w*j+i] = t2;
                }
            }
        }
        else
        {
            DBG_Printf ("SetTexture(bad format) %d\n", pTexInfo->GR_format);
            return;
        }

        tex_downloaded = next_texture_id++;
        pTexInfo->downloaded = tex_downloaded;
        glBindTexture( GL_TEXTURE_2D, tex_downloaded );

#ifdef MINI_GL_COMPATIBILITY
        //if (pTexInfo->GR_format==GR_TEXFMT_ALPHA_INTENSITY_88)
        //    glTexImage2D( GL_TEXTURE_2D, 0, GL_LUMINANCE_ALPHA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, ptex );
        //else
            if (min_filter & MIPMAP_MASK)
                gluBuild2DMipmaps( GL_TEXTURE_2D, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, ptex );
            else
                glTexImage2D( GL_TEXTURE_2D, 0, 4, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, ptex );
#else
#ifdef USE_PALETTED_TEXTURE
            //Hurdler: not really supported and not tested recently
        if( usePalettedTexture
            && (pTexInfo->GR_format==GR_TEXFMT_P_8)
            && !(pTexInfo->flags & TF_CHROMAKEYED) )
        {
            glColorTableEXT(GL_TEXTURE_2D, GL_RGB8, 256, GL_RGB, GL_UNSIGNED_BYTE, palette_tex);
            glTexImage2D( GL_TEXTURE_2D, 0, GL_COLOR_INDEX8_EXT, w, h, 0, GL_COLOR_INDEX, GL_UNSIGNED_BYTE, pTexInfo->GR_data );
        }
        else
#endif
        if( pTexInfo->GR_format==GR_TEXFMT_ALPHA_INTENSITY_88 )
        {
            //glTexImage2D( GL_TEXTURE_2D, 0, GL_ALPHA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, ptex );
            if (min_filter & MIPMAP_MASK)
                gluBuild2DMipmaps( GL_TEXTURE_2D, GL_LUMINANCE_ALPHA, w, h, GL_RGBA, GL_UNSIGNED_BYTE, ptex );
            else
                glTexImage2D( GL_TEXTURE_2D, 0, GL_LUMINANCE_ALPHA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, ptex );
        }
        else 
        {
            if (min_filter & MIPMAP_MASK)
                gluBuild2DMipmaps( GL_TEXTURE_2D, textureformatGL, w, h, GL_RGBA, GL_UNSIGNED_BYTE, ptex );
            else
                glTexImage2D( GL_TEXTURE_2D, 0, textureformatGL, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, ptex );
        }
#endif

        if( pTexInfo->tfflags & TF_WRAPX )
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
        else
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP);

        if( pTexInfo->tfflags & TF_WRAPY )
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
        else
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP);

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mag_filter);
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min_filter);

        pTexInfo->nextmipmap = NULL;
        if (gr_cachetail) { // insertion en fin de liste
            gr_cachetail->nextmipmap = pTexInfo;
            gr_cachetail = pTexInfo;
        }
        else // initialisation de la liste
            gr_cachetail = gr_cachehead =  pTexInfo;
    }

#ifdef MINI_GL_COMPATIBILITY
    switch(pTexInfo->flags)
    {
        case 0 :
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP);
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP);
            break;
        default:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
            break;
    }
#endif
}

//int num_drawn_poly;

// -----------------+
// DrawPolygon      : Render a polygon, set the texture, set render mode
// -----------------+
EXPORT void HWRAPI( DrawPolygon ) ( FSurfaceInfo_t  *pSurf,
                                    //FTextureInfo_t  *pTexInfo,
                                    vxtx3d_t      *pOutVerts,
                                    FUINT         iNumPts,
                                    FBITFIELD     polyflags )
{
    FUINT i, j;
    RGBA_float_t c;

    //num_drawn_poly += iNumPts-2;

    // DrawPolygon is invoked by GenPrint, so cannot use GenPrint here.
#ifdef MINI_GL_COMPATIBILITY
    if (polyflags & PF_Corona) 
        polyflags &= ~PF_NoDepthTest;
#else
    if( (polyflags & PF_Corona) && (oglflags & GLF_NOZBUFREAD) )
        polyflags &= ~(PF_NoDepthTest|PF_Corona);
#endif

    SetBlend( polyflags );    //TODO: inline (#pragma..)

    // If Modulated, mix the surface colour to the texture
    if( (cur_polyflags & PF_Modulated) && pSurf)
    {
        if (tint_color_id)
        {
            // Imitate the damage, and special object palette tints
            c.red   = (tint_rgb.red   + to_glcolor_float[pSurf->FlatColor.s.red])  /2.0f;
            c.green = (tint_rgb.green + to_glcolor_float[pSurf->FlatColor.s.green])/2.0f;
            c.blue  = (tint_rgb.blue  + to_glcolor_float[pSurf->FlatColor.s.blue]) /2.0f;
            c.alpha = to_glcolor_float[pSurf->FlatColor.s.alpha];
        }
        else
        {
            c.red   = to_glcolor_float[pSurf->FlatColor.s.red];
            c.green = to_glcolor_float[pSurf->FlatColor.s.green];
            c.blue  = to_glcolor_float[pSurf->FlatColor.s.blue];
            c.alpha = to_glcolor_float[pSurf->FlatColor.s.alpha];
        }
#ifdef MINI_GL_COMPATIBILITY
        glColor4f(c.red, c.green, c.blue, c.alpha);
#else
        glColor4fv( (float *)&c );    // is in RGBA float format
#endif
    }

    // this test is added for new coronas' code (without depth buffer)
    // I think I should do a separate function for drawing coronas, so it will be a little faster
#ifndef MINI_GL_COMPATIBILITY
    if (polyflags & PF_Corona) // check to see if we need to draw the corona
    {
        //rem: all 8 (or 8.0f) values are hard coded: it can be changed to a higher value
        GLfloat     buf[8][8];
        GLdouble    cx, cy, cz;
        GLdouble    px, py, pz;
        GLfloat     scalef = 0;

        cx = (pOutVerts[0].x + pOutVerts[2].x) / 2.0f; // we should change the coronas' ...
        cy = (pOutVerts[0].y + pOutVerts[2].y) / 2.0f; // ... code so its only done once.
        cz = pOutVerts[0].z;

        // I dont know if this is slow or not
        gluProject(cx, cy, cz, modelMatrix, projMatrix, viewport, &px, &py, &pz);
        //DBG_Printf("Projection: (%f, %f, %f)\n", px, py, pz);

        if ( (pz <  0.0) ||
             (px < -8.0) ||
             (py < viewport[1]-8.0) ||
             (px > viewport[2]+8.0) ||
             (py > viewport[1]+viewport[3]+8.0))
            return;

        // the damned slow glReadPixels functions :(
        glReadPixels( (int)px-4, (int)py, 8, 8, GL_DEPTH_COMPONENT, GL_FLOAT, buf );
        //DBG_Printf("DepthBuffer: %f %f\n", buf[0][0], buf[3][3]);

        // count pixels that are closer
        for (i=0; i<8; i++)
        {
            for (j=0; j<8; j++)
                scalef += ( buf[i][j] < (pz - 0.00005f) )? 0 : 1;
        }

        // quick test for screen border (not 100% correct, but looks ok)
        if (px < 4) scalef -= 8*(4-px);
        if (py < viewport[1]+4) scalef -= 8*(viewport[1]+4-py);
        if (px > viewport[2]-4) scalef -= 8*(4-(viewport[2]-px));
        if (py > viewport[1]+viewport[3]-4) scalef -= 8*(4-(viewport[1]+viewport[3]-py));

        scalef /= 64;
        //DBG_Printf("Scale factor: %f\n", scalef);

        if (scalef < 0.05f) // �a sert � rien de tracer la light
            return;

        c.alpha *= scalef; // change the alpha value (it seems better than changing the size of the corona)
        glColor4fv( (float *)&c );
    }
#endif
    if (polyflags & PF_MD2) 
        return;

    glBegin( GL_TRIANGLE_FAN );
    for( i=0; i<iNumPts; i++ )
    {
        glTexCoord2f( pOutVerts[i].sow, pOutVerts[i].tow );
        //Hurdler: test code: -pOutVerts[i].z => pOutVerts[i].z
        glVertex3f( pOutVerts[i].x, pOutVerts[i].y, pOutVerts[i].z );
        //glVertex3f( pOutVerts[i].x, pOutVerts[i].y, -pOutVerts[i].z );
    }
    glEnd();
}


// ==========================================================================
//
// ==========================================================================
EXPORT void HWRAPI( SetSpecialState ) (hwd_specialstate_e IdState, int Value)
{
    switch (IdState)
    {
        case HWD_MIRROR_77: {
            //08/01/00: Hurdler this is a test for mirror
            if (!Value)
                ClearBuffer( false, true, 0 ); // clear depth buffer
            break;
        }

        case HWD_SET_TINT_COLOR: {
            tint_color_id = Value;
            tint_rgb.blue  = to_glcolor_float[((Value>>16)&0xff)];
            tint_rgb.green = to_glcolor_float[((Value>>8)&0xff)];
            tint_rgb.red   = to_glcolor_float[((Value)&0xff)];
            break;
        }

        case HWD_SET_FOG_COLOR: {
            GLfloat fogcolor[4];

            fogcolor[0] = to_glcolor_float[((Value>>16)&0xff)];
            fogcolor[1] = to_glcolor_float[((Value>>8)&0xff)];
            fogcolor[2] = to_glcolor_float[((Value)&0xff)];
            fogcolor[3] = 0x0;
            glFogfv(GL_FOG_COLOR, fogcolor);
            break;
        }
        case HWD_SET_FOG_DENSITY:
            glFogf(GL_FOG_DENSITY, Value*1200/(500*1000000.0f));
            break;

        case HWD_SET_FOG_MODE:
            if (Value)
            {
                glEnable(GL_FOG);
                // experimental code
                /*
                switch (Value)
                {
                    case 1:
                        glFogi(GL_FOG_MODE, GL_LINEAR);
                        glFogf(GL_FOG_START, -1000.0f);
                        glFogf(GL_FOG_END, 2000.0f);
                        break;
                    case 2:
                        glFogi(GL_FOG_MODE, GL_EXP);
                        break;
                    case 3:
                        glFogi(GL_FOG_MODE, GL_EXP2);
                        break;
                }
                */
            }
            else
                glDisable(GL_FOG);
            break;

        case HWD_SET_POLYGON_SMOOTH:
            if (Value)
                glEnable(GL_POLYGON_SMOOTH);
            else
                glDisable(GL_POLYGON_SMOOTH);
            break;

        case HWD_SET_TEXTUREFILTERMODE:
            switch (Value) 
            {
                case HWD_SET_TEXTUREFILTER_TRILINEAR:
                    min_filter = mag_filter = GL_LINEAR_MIPMAP_LINEAR;
                    break;
                case HWD_SET_TEXTUREFILTER_BILINEAR :
                    min_filter = mag_filter = GL_LINEAR;
                    break;
                case HWD_SET_TEXTUREFILTER_POINTSAMPLED :
                    min_filter = mag_filter = GL_NEAREST;
                    break;
                case HWD_SET_TEXTUREFILTER_MIXED1 :
                    mag_filter = GL_LINEAR;
                    min_filter = GL_NEAREST;
                    break;
                case HWD_SET_TEXTUREFILTER_MIXED2 :
                    mag_filter = GL_NEAREST;
                    min_filter = GL_LINEAR;
                    break;
            }
            VIDGL_Flush_GL_textures(); //??? if we want to change filter mode by texture, remove this

        default:
            break;
    }
}

FTransform_t  md2_transform;

// -----------------+
// HWRAPI DrawMD2   : Draw an MD2 model with glcommands
// -----------------+
//EXPORT void HWRAPI( DrawMD2 ) (md2_model_t *model, int frame)
EXPORT void HWRAPI( DrawMD2 ) (int *gl_cmd_buffer, md2_frame_t *frame,
                               FTransform_t *pos, float scale)
{
    int     val, count, index;
    GLfloat s, t;

    //TODO: Maybe we can put all this in a display list the first time it's
    //      called and after, use this display list: faster (how much?) but
    //      require more memory (how much?)

    DrawPolygon( NULL, NULL, 0, PF_Masked|PF_Modulated|PF_Occlude|PF_Clip);

    glPushMatrix(); // should be the same as glLoadIdentity
    //Hurdler: now it seems to work
    glTranslatef(pos->x, pos->z, pos->y);
    glRotatef(pos->angley, 0.0f, -1.0f, 0.0f);
    glRotatef(pos->anglex, -1.0f, 0.0f, 0.0f);
    glScalef(scale, scale, scale);

    val = *gl_cmd_buffer++;

    while (val != 0)
    {
        if (val < 0)
        {
            glBegin (GL_TRIANGLE_FAN);
            count = -val;
        }
        else
        {
            glBegin (GL_TRIANGLE_STRIP);
            count = val;
        }

        while (count--)
        {
            s = *(float *) gl_cmd_buffer++;
            t = *(float *) gl_cmd_buffer++;
            index = *gl_cmd_buffer++;

            glTexCoord2f (s, t);
            glVertex3f (frame->vertices[index].vertex[0]/2.0f,
                        frame->vertices[index].vertex[1]/2.0f,
                        frame->vertices[index].vertex[2]/2.0f);
        }

        glEnd ();

        val = *gl_cmd_buffer++;
    }
    glPopMatrix(); // should be the same as glLoadIdentity
}

// -----------------+
// SetTransform     : 
// -----------------+
EXPORT void HWRAPI( SetTransform ) (FTransform_t *transform)
{
    static int special_splitscreen;

    glLoadIdentity();
    if (transform)
    {
        // keep a trace of the transformation for md2
        memcpy(&md2_transform, transform, sizeof(md2_transform));
        glScalef(transform->scalex, transform->scaley, -transform->scalez);
        glRotatef(transform->anglex       , 1.0, 0.0, 0.0);
        glRotatef(transform->angley+270.0f, 0.0, 1.0, 0.0);
        glTranslatef(-transform->x, -transform->z, -transform->y);

        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        special_splitscreen = (transform->splitscreen && transform->fovxangle==90.0f);
        if (special_splitscreen)
        {
            gluPerspective( 53.13, 2*ASPECT_RATIO,  // 53.13 = 2*atan(0.5)
                            near_clipping_plane, FAR_CLIPPING_PLANE);
        }
        else
        {
            gluPerspective( transform->fovxangle, ASPECT_RATIO, near_clipping_plane, FAR_CLIPPING_PLANE);
        }
#ifndef MINI_GL_COMPATIBILITY
        glGetDoublev(GL_PROJECTION_MATRIX, projMatrix); // added for new coronas' code (without depth buffer)
#endif
        glMatrixMode(GL_MODELVIEW);
    }
    else
    {
        glScalef(1.0, 1.0f, -1.0f);

        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        if (special_splitscreen)
        {
            gluPerspective( 53.13, 2*ASPECT_RATIO,  // 53.13 = 2*atan(0.5)
                            near_clipping_plane, FAR_CLIPPING_PLANE);
        }
        else
        {
            //Hurdler: is "fov" correct?
            gluPerspective( fov, ASPECT_RATIO, near_clipping_plane, FAR_CLIPPING_PLANE);
        }
#ifndef MINI_GL_COMPATIBILITY
        glGetDoublev(GL_PROJECTION_MATRIX, projMatrix); // added for new coronas' code (without depth buffer)
#endif
        glMatrixMode(GL_MODELVIEW);
    }

#ifndef MINI_GL_COMPATIBILITY
    glGetDoublev(GL_MODELVIEW_MATRIX, modelMatrix); // added for new coronas' code (without depth buffer)
#endif
}

EXPORT int  HWRAPI( GetTextureUsed ) (void)
{
    FTextureInfo_t* tmp = gr_cachehead;
    int             res = 0;

    while (tmp)
    {
        res += tmp->height*tmp->width*(screen_depth/8);
        tmp = tmp->nextmipmap;
    }
    return res;
}

EXPORT int  HWRAPI( GetRenderVersion ) (void)
{
#if 1
    // version of component compile
    return DOOMLEGACY_COMPONENT_VERSION;
#else
    // version of renderer
    int vernum = 0;
    const char * verstr = glGetString(GL_VERSION);
    if( verstr )
       vernum = atoi( verstr );
    return vernum;
#endif
}

// Only i_video_xshm is using this API,
// all the other ports call glGetString, and set oglflags accordingly
EXPORT char *HWRAPI( GetRenderer ) (void)
{
    const GLubyte * renstr = glGetString(GL_RENDERER);
  
    rendererString[0] = '\0';
    if( renstr )
       strncpy(rendererString, (char*)renstr, 255);
    rendererString[255] = '\0';

    return rendererString;
}
