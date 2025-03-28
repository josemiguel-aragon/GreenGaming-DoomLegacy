// Emacs style mode select   -*- C++ -*- 
//-----------------------------------------------------------------------------
//
// $Id: p_telept.c 1481 2019-12-13 05:16:17Z wesleyjohnson $
//
// Copyright (C) 1993-1996 by id Software, Inc.
// Copyright (C) 1998-2011 by DooM Legacy Team.
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
// $Log: p_telept.c,v $
// Revision 1.8  2001/08/06 23:57:09  stroggonmeth
// Removed portal code, improved 3D floors in hardware mode.
//
// Revision 1.7  2001/03/13 22:14:19  stroggonmeth
// Long time no commit. 3D floors, FraggleScript, portals, ect.
//
// Revision 1.6  2001/01/25 22:15:44  bpereira
// added heretic support
//
// Revision 1.5  2000/11/04 16:23:43  bpereira
//
// Revision 1.4  2000/11/02 17:50:09  stroggonmeth
// Big 3Dfloors & FraggleScript commit!!
//
// Revision 1.3  2000/04/04 00:32:47  stroggonmeth
// Initial Boom compatability plus few misc changes all around.
//
// Revision 1.2  2000/02/27 00:42:10  hurdler
// Revision 1.1.1.1  2000/02/22 20:32:32  hurdler
// Initial import into CVS (v1.29 pr3)
//
//
// DESCRIPTION:
//      Teleportation.
//
//-----------------------------------------------------------------------------

#include "doomincl.h"
#include "p_local.h"
#include "p_tick.h"
  // think
#include "g_game.h"
#include "r_state.h"
#include "r_main.h"
  //SoM: 3/16/2000
#include "s_sound.h"



boolean P_Teleport(mobj_t *thing, fixed_t x, fixed_t y, angle_t angle)
{
    mobj_t*     fog;
    fixed_t     oldx = thing->x;
    fixed_t     oldy = thing->y;
    fixed_t     oldz = thing->z;
    fixed_t     aboveFloor;
    fixed_t     fogDelta = 0;

    // no voodoo player effects
    player_t * player = (thing->player && thing->player->mo == thing) ?
          thing->player : NULL;

    if( EN_heretic && !(thing->flags&MF_MISSILE))
        fogDelta = TELEFOGHEIGHT;
    aboveFloor = thing->z - thing->floorz;
    
    if (!P_TeleportMove (thing, x, y, false))
        return 0;
    
    thing->z = thing->floorz;  //fixme: not needed?
    if (player)
    {
        // heretic code
        if(player->powers[pw_flight] && aboveFloor)
        {
            thing->z = thing->floorz+aboveFloor;
            if(thing->z+thing->height > thing->ceilingz)
                thing->z = thing->ceilingz - thing->height;
            player->viewz = thing->z+player->viewheight;
        }
        else
            player->viewz = thing->z+player->viewheight;
    }
    else if(thing->flags&MF_MISSILE) // heretic stuff
    {
        thing->z = thing->floorz+aboveFloor;
        if(thing->z+thing->height > thing->ceilingz)
            thing->z = thing->ceilingz - thing->height;
    }
    
    // spawn teleport fog at source and destination
    fog = P_SpawnMobj (oldx, oldy, oldz+fogDelta, MT_TFOG);
    S_StartObjSound(fog, sfx_telept);

    angle_t angf = ANGLE_TO_FINE(angle);  // fine angle, used later
    fog = P_SpawnMobj (x+20*finecosine[angf], y+20*finesine[angf],
          thing->z+fogDelta, MT_TFOG);
    
    // emit sound, where?
    S_StartObjSound(fog, sfx_telept);
    
    // don't move for a bit
    if (player)
    {
        if( !player->powers[pw_weaponlevel2] )  // not heretic
            thing->reactiontime = 18;
        // added : absolute angle position
        if(thing== consoleplayer_ptr->mo)
            localangle[0] = angle;
        if(displayplayer2_ptr && thing== displayplayer2_ptr->mo) // NULL when unused
            localangle[1] = angle;

#ifdef CLIENTPREDICTION2
        if(thing== consoleplayer_ptr->mo)
        {
            consoleplayer_ptr->spirit->reactiontime = thing->reactiontime;
            CL_ResetSpiritPosition(thing);
        }
#endif
        // [WDJ] kill bob momentum or player will keep bobbing for a while
        player->bob_momx = player->bob_momy = 0;

        // move chasecam at new player location
        if ( camera.chase == player )
            P_ResetCamera (player);
    }
    
    thing->angle = angle;
    if( EN_heretic
        && thing->flags2&MF2_FOOTCLIP
        && P_GetThingFloorType(thing) != FLOOR_SOLID )
    {
        thing->flags2 |= MF2_FEETARECLIPPED;
    }
    else if(thing->flags2&MF2_FEETARECLIPPED)
    {
        thing->flags2 &= ~MF2_FEETARECLIPPED;
    }
    if(thing->flags&MF_MISSILE)
    {
        thing->momx = FixedMul(thing->info->speed, finecosine[angf]);
        thing->momy = FixedMul(thing->info->speed, finesine[angf]);
    }
    else
        thing->momx = thing->momy = thing->momz = 0;
    
    return 1;
}

// =========================================================================
//                            TELEPORTATION
// =========================================================================

int EV_Teleport ( line_t*       line,
                  int           side,
                  mobj_t*       thing )
{
    int         i;
    int         tag;
    mobj_t*     m;
    thinker_t*  thinker;
    sector_t*   sector;

    // don't teleport missiles
    if ( (EN_doom_etc && (thing->flags & MF_MISSILE)) 
        || (thing->flags2 & MF2_NOTELEPORT) )  // heretic flag
        return 0;

    // Don't teleport if hit back of line,
    //  so you can get out of teleporter.
    if (side == 1)
        return 0;


    tag = line->tag;
    for (i = 0; i < numsectors; i++)
    {
        if (sectors[ i ].tag == tag )
        {
            thinker = thinkercap.next;
            for (thinker = thinkercap.next;
                 thinker != &thinkercap;
                 thinker = thinker->next)
            {
                // not a mobj
                if (thinker->function.acp1 != (actionf_p1)P_MobjThinker)
                    continue;

                m = (mobj_t *)thinker;

                // not a teleportman
                if (m->type != MT_TELEPORTMAN )
                    continue;

                sector = m->subsector->sector;
                // wrong sector
                if (sector-sectors != i )
                    continue;

                return P_Teleport(thing, m->x, m->y, m->angle);
            }
        }
    }
    return 0;
}




/*
  SoM: 3/15/2000
  Added new boom teleporting functions.
*/
int EV_SilentTeleport(line_t *line, int side, mobj_t *thing)
{
  int       i;
  mobj_t    *m;
  thinker_t *th;

  // don't teleport missiles
  // Don't teleport if hit back of line,
  // so you can get out of teleporter.

  if (side || thing->flags & MF_MISSILE)
    return 0;

  for (i = -1; (i = P_FindSectorFromLineTag(line, i)) >= 0;)
  {
    for (th = thinkercap.next; th != &thinkercap; th = th->next)
    {
      if (th->function.acp1 == (actionf_p1) P_MobjThinker &&
          (m = (mobj_t *) th)->type == MT_TELEPORTMAN  &&
          m->subsector->sector-sectors == i)
      {
          // Height of thing above ground, in case of mid-air teleports:
          fixed_t z = thing->z - thing->floorz;

          // Get the angle between the exit thing and source linedef.
          // Rotate 90 degrees, so that walking perpendicularly across
          // teleporter linedef causes thing to exit in the direction
          // indicated by the exit thing.
          angle_t angle =
            R_PointToAngle2(0, 0, line->dx, line->dy) - m->angle + ANG90;

          // Sine, cosine of angle adjustment
          fixed_t sin_taa = sine_ANG(angle);
          fixed_t cos_taa = cosine_ANG(angle);

          // Momentum of thing crossing teleporter linedef
          fixed_t momx = thing->momx;
          fixed_t momy = thing->momy;

          // Whether this is a player, and if so, a pointer to its player_t
          player_t *player = thing->player;

          // Attempt to teleport, aborting if blocked
          if (!P_TeleportMove(thing, m->x, m->y, false))
            return 0;

          // Rotate thing according to difference in angles
          thing->angle += angle;

          // Adjust z position to be same height above ground as before
          thing->z = z + thing->floorz;

          // Rotate thing's momentum to come out of exit just like it entered
          thing->momx = FixedMul(momx, cos_taa) - FixedMul(momy, sin_taa);
          thing->momy = FixedMul(momy, cos_taa) + FixedMul(momx, sin_taa);

          // Adjust player's view, in case there has been a height change
          // Voodoo dolls are excluded by making sure player->mo == thing.
          if (player && player->mo == thing)
          {
              // Save the current deltaviewheight, used in stepping
              fixed_t deltaviewheight = player->deltaviewheight;

              // Clear deltaviewheight, since we don't want any changes
              player->deltaviewheight = 0;

              // Set player's view according to the newly set parameters
              P_CalcHeight(player);

              // Reset the delta to have the same dynamics as before
              player->deltaviewheight = deltaviewheight;

              // SoM: 3/15/2000: move chasecam at new player location
              if ( camera.chase == player )
                 P_ResetCamera (player);

          }
          return 1;
      }
    }
  }
  return 0;
}

//
// Silent linedef-based TELEPORTATION, by Lee Killough
// Primarily for rooms-over-rooms etc.
// This is the complete player-preserving kind of teleporter.
// It has advantages over the teleporter with thing exits.
//

// maximum fixed_t units to move object to avoid hiccups
#define FUDGEFACTOR 10

int EV_SilentLineTeleport(line_t *line, int side, mobj_t *thing,
                          boolean reverse)
{
  int i;
  line_t *l;

  if (side || thing->flags & MF_MISSILE)
    return 0;

  for (i = -1; (i = P_FindLineFromLineTag(line, i)) >= 0;)
  {
    if ((l=lines+i) != line && l->backsector)
    {
        // Get the thing's position along the source linedef
        fixed_t pos = abs(line->dx) > abs(line->dy) ?
          FixedDiv(thing->x - line->v1->x, line->dx) :
          FixedDiv(thing->y - line->v1->y, line->dy) ;

        // Get the angle between the two linedefs, for rotating
        // orientation and momentum. Rotate 180 degrees, and flip
        // the position across the exit linedef, if reversed.
        angle_t angle = (reverse ? pos = FRACUNIT-pos, 0 : ANG180) +
          R_PointToAngle2(0, 0, l->dx, l->dy) -
          R_PointToAngle2(0, 0, line->dx, line->dy);

        // Interpolate position across the exit linedef
        fixed_t x = l->v2->x - FixedMul(pos, l->dx);
        fixed_t y = l->v2->y - FixedMul(pos, l->dy);

        // Sine, cosine of angle adjustment
        fixed_t sin_taa = sine_ANG(angle);
        fixed_t cos_taa = cosine_ANG(angle);

        // Maximum distance thing can be moved away from interpolated
        // exit, to ensure that it is on the correct side of exit linedef
        int fudge = FUDGEFACTOR;

        // Whether this is a player, and if so, a pointer to its player_t.
        // Voodoo dolls are excluded by making sure thing->player->mo==thing.
        player_t * player = (thing->player && thing->player->mo == thing) ?
          thing->player : NULL;

        // Whether walking towards first side of exit linedef steps down
        int stepdown =
          l->frontsector->floorheight < l->backsector->floorheight;

        // Height of thing above ground
        fixed_t z = thing->z - thing->floorz;

        // Side to exit the linedef on positionally.
        //
        // Notes:
        //
        // This flag concerns exit position, not momentum. Due to
        // roundoff error, the thing can land on either the left or
        // the right side of the exit linedef, and steps must be
        // taken to make sure it does not end up on the wrong side.
        //
        // Exit momentum is always towards side 1 in a reversed
        // teleporter, and always towards side 0 otherwise.
        //
        // Exiting positionally on side 1 is always safe, as far
        // as avoiding oscillations and stuck-in-wall problems,
        // but may not be optimum for non-reversed teleporters.
        //
        // Exiting on side 0 can cause oscillations if momentum
        // is towards side 1, as it is with reversed teleporters.
        //
        // Exiting on side 1 slightly improves player viewing
        // when going down a step on a non-reversed teleporter.

        int side = reverse || (player && stepdown);

        // Make sure we are on correct side of exit linedef.
        while (P_PointOnLineSide(x, y, l) != side && --fudge>=0)
          if (abs(l->dx) > abs(l->dy))
            y -= ((l->dx < 0) != side) ? -1 : 1;
          else
            x += ((l->dy < 0) != side) ? -1 : 1;

        // Attempt to teleport, aborting if blocked
        if (!P_TeleportMove(thing, x, y, false))
          return 0;

        // Adjust z position to be same height above ground as before.
        // Ground level at the exit is measured as the higher of the
        // two floor heights at the exit linedef.
        thing->z = z + sides[l->sidenum[stepdown]].sector->floorheight;

        // Rotate thing's orientation according to difference in linedef angles
        thing->angle += angle;

        // Momentum of thing crossing teleporter linedef
        x = thing->momx;
        y = thing->momy;

        // Rotate thing's momentum to come out of exit just like it entered
        thing->momx = FixedMul(x, cos_taa) - FixedMul(y, sin_taa);
        thing->momy = FixedMul(y, cos_taa) + FixedMul(x, sin_taa);

        // Adjust a player's view, in case there has been a height change
        if (player)
        {
            // Save the current deltaviewheight, used in stepping
            fixed_t deltaviewheight = player->deltaviewheight;

            // Clear deltaviewheight, since we don't want any changes now
            player->deltaviewheight = 0;

            // Set player's view according to the newly set parameters
            P_CalcHeight(player);

            // Reset the delta to have the same dynamics as before
            player->deltaviewheight = deltaviewheight;

            // SoM: 3/15/2000: move chasecam at new player location
            if ( camera.chase == player )
               P_ResetCamera (player);
        }

        return 1;
    }
  }
  return 0;
}

