from __future__ import (print_function, absolute_import)

import io
import collections

from smoke.io.wrap import demo as io_wrp_dm
from smoke.replay import demo as rply_dm
from smoke.replay.const import Data


with io.open('1481687622.dem', 'rb') as infile:
    demo_io = io_wrp_dm.Wrap(infile)
    demo_io.bootstrap()

    # parse = Data.UserMessages | Data.GameEvents
    demo = rply_dm.Demo(demo_io, parse=Data.All)
    demo.bootstrap()

    class_info = demo.match.class_info
    messages_found = collections.Counter()
    events_found = collections.Counter()

    game_meta_tables = demo.match.recv_tables.by_dt['DT_DOTAGamerulesProxy']
    game_status_index = game_meta_tables.by_name['dota_gamerules_data.m_nGameState']
    
    points = []
    for i, match in enumerate(demo.play()):
        game_meta = match.entities.by_cls[class_info['DT_DOTAGamerulesProxy']][0].state
        current_game_status = game_meta.get(game_status_index)
        if current_game_status != 5:
            continue
            
        world_data = match.entities.by_cls[class_info['DT_DOTA_PlayerResource']]
        current_data = world_data[0].state

        npc_info_table = match.recv_tables.by_dt['DT_DOTA_BaseNPC']
        position_offset_x = npc_info_table.by_name['m_cellX']
        position_offset_y = npc_info_table.by_name['m_cellY']
        position_origin_v = npc_info_table.by_name['m_vecOrigin']

        player_resource = match.recv_tables.by_dt['DT_DOTA_PlayerResource']
        
        for idx in range(10):
            team_id = player_resource.by_name['m_iPlayerTeams.%04d' % idx]
            hero_id = player_resource.by_name['m_hSelectedHero.%04d' % idx]
            team, hero_handle = current_data.get(team_id), current_data.get(hero_id)

            try:
                if hero_handle:
                    hero = match.entities.by_ehandle[hero_handle].state

                    x = hero.get(position_offset_x) + hero.get(position_origin_v)[0] / 128.
                    y = hero.get(position_offset_y) + hero.get(position_origin_v)[1] / 128.
                    points.append((x,y))
            except KeyError:
                pass

            # lh = current_data.get(player_resource.by_name['m_iLastHitCount.{:04d}'.format(idx)])
            # deaths = current_data.get(player_resource.by_name['m_iDeaths.{:04d}'.format(idx)])
            # print(lh, '/', deaths, end=', ')
        # print('')
        
        messages_found.update(match.user_messages.keys())
        for k, v in match.user_messages.items():
            pass
            # messages_found.add(k)
            # if k in (67, 68): # (77, 78, 83, 85, 86, 88, 89, 97): # 68
            #     print('FRAME', i, 'KEY', k, 'VALUE', dir(v[0]))
            #     break
            
        events_found.update(match.game_events.keys())            
        for idx, lst in match.game_events.items():
            # match.game_event_descriptors.by_eventid[idx]
            # print(match.game_event_descriptors.by_eventid[idx])
            break
    
    # print(messages_found)
    # print(events_found)

    # demo.finish()
    # print(demo.match.overview)


import matplotlib.pyplot as plt

plt.clf()
plt.scatter([x for x,_ in points], [y for _,y in points]) #, color='blue')
plt.show()
