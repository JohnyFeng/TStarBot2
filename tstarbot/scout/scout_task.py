from tstarbot.data.pool import macro_def as md
from tstarbot.data.pool import scout_pool as sp
from s2clientprotocol import sc2api_pb2 as sc_pb
import pysc2.lib.typeenums as tp

MAX_SCOUT_HISTORY = 10
SCOUT_BASE_RANGE = 15
SCOUT_SAFE_RANGE = 12
SCOUT_CRUISE_RANGE = 5
SCOUT_CRUISE_ARRIVAED_RANGE = 1

class ScoutTask(object):
    def __init__(self, scout, home):
        self._scout = scout
        self._home = home
        self._status = md.ScoutTaskStatus.INIT
        self._last_health = None

    def scout(self):
        return self._scout

    def type(self):
        raise NotImplementedError

    def status(self):
        return self._status

    def do_task(self, view_enemys, dc):
        return self._do_task_inner(view_enemys, dc)

    def post_process(self):
        raise NotImplementedError

    def _do_task_inner(self, view_enemys, dc):
        raise NotImplementedError

    def _move_to_target(self, pos):
        action = sc_pb.Action()
        action.action_raw.unit_command.ability_id = tp.ABILITY_ID.SMART.value
        action.action_raw.unit_command.target_world_space_pos.x = pos[0]
        action.action_raw.unit_command.target_world_space_pos.y = pos[1]
        action.action_raw.unit_command.unit_tags.append(self._scout.unit().tag)
        return action

    def _move_to_home(self):
        action = sc_pb.Action()
        action.action_raw.unit_command.ability_id = tp.ABILITY_ID.SMART.value
        action.action_raw.unit_command.target_world_space_pos.x = self._home[0]
        action.action_raw.unit_command.target_world_space_pos.y = self._home[1]
        action.action_raw.unit_command.unit_tags.append(self._scout.unit().tag)
        return action

    def _noop(self):
        action = sc_pb.Action()
        action.action_raw.unit_command.ability_id = tp.ABILITY_ID.INVALID.value
        return action

    def _detect_attack(self):
        attack = False
        current_health = self._scout.unit().float_attr.health
        if self._last_health is None:
            self._last_health = current_health
            return attack

        if self._last_health > current_health:
            #print('scout is attack')
            attack = True

        self._last_health = current_health
        return attack

    def _detect_recovery(self):
        curr_health = self._scout.unit().float_attr.health
        max_health = self._scout.unit().float_attr.health_max
        return curr_health == max_health

    def _check_scout_lost(self):
        return self._scout.is_lost()

EXPLORE_V1 = 0
EXPLORE_V2 = 1

class ScoutExploreTask(ScoutTask):
    def __init__(self, scout, target, home, version):
        super(ScoutExploreTask, self).__init__(scout, home)
        self._target = target
        self._status = md.ScoutTaskStatus.DOING
        self._monitor_pos = self._get_monitor_pos()
        self._base_arrived = False
        self._monitor_arrived = False
        self._version = version
        #print('SCOUT task, base_pos={} monitor_pos={}'.format(
        #    self._target.pos, self._monitor_pos))

    def type(self):
        return md.ScoutTaskType.EXPORE

    def target(self):
        return self._target

    def post_process(self):
        self._target.has_scout = False
        self._scout.is_doing_task = False
        if self._status == md.ScoutTaskStatus.SCOUT_DESTROY:
            if self._check_in_target_range() and not self._judge_task_done():
                self._target.has_enemy_base = True
                self._target.has_army = True
            #print('SCOUT explore_task post destory; target=', str(self._target))
        elif self._status == md.ScoutTaskStatus.UNDER_ATTACK:
            if self._check_in_base_range() and not self._judge_task_done():
                self._target.has_enemy_base = True
                self._target.has_army = True
            #print('SCOUT explore_task post attack; target=', str(self._target))
        else:
            #print('SCOUT task post_process, status=', self._status, ';target=', str(self._target))
            pass

    def _do_task_inner(self, view_enemys, dc):
        if self._check_scout_lost():
            #print('SCOUT scout is lost, no action, tag=', self._scout.unit().tag)
            self._status = md.ScoutTaskStatus.SCOUT_DESTROY
            return None

        if self._check_attack():
            return self._exec_by_status()

        if self._detect_enemy(view_enemys, dc):
            self._status = md.ScoutTaskStatus.DONE
            return self._move_to_home()

        if not self._base_arrived and self._check_in_base_range():
            self._base_arrived = True

        if not self._monitor_arrived and self._check_in_monitor_range():
            self._monitor_arrived = True

        return self._exec_by_status()

    def _exec_explore(self):
        if self._version == EXPLORE_V1:
            if not self._base_arrived:
                return self._move_to_target(self._target.pos)
            elif self._judge_task_done():
                self._status == md.ScoutTaskStatus.DONE
                return self._move_to_home()
            else:
                return self._noop()
        else:
            if not self._base_arrived:
                return self._move_to_target(self._target.pos)
            elif not self._monitor_arrived and self._judge_task_done():
                return self._move_to_target(self._monitor_pos)
            else:
                return self._noop()

    def _exec_by_status(self):
        if self._status == md.ScoutTaskStatus.DOING:
            return self._exec_explore()
        elif self._status == md.ScoutTaskStatus.DONE:
            return self._move_to_home()
        elif self._status == md.ScoutTaskStatus.UNDER_ATTACK:
            return self._move_to_home()
        else:
            print('SCOUT exec noop, scout status=', self._status)
            return self._noop()

    def _detect_enemy(self, view_enemys, dc):
        bases = []
        queues = []
        airs = []
        armys = []
        main_base_buildings = []
        for enemy in view_enemys:
            if enemy.unit_type in md.BASE_UNITS:
                bases.append(enemy)
            elif enemy.unit_type == md.UNIT_TYPEID.ZERG_QUEEN.value:
                queues.append(enemy)
            elif enemy.unit_type in md.COMBAT_UNITS:
                armys.append(enemy)
            elif enemy.unit_type in md.COMBAT_AIR_UNITS:
                armys.append(enemy)
            elif enemy.unit_type in md.MAIN_BASE_BUILDS:
                main_base_buildings.append(enemy)
            else:
                continue

        goback = False
        for base in bases:
            dist = md.calculate_distance(self._target.pos[0], 
                                         self._target.pos[1],
                                         base.float_attr.pos_x,
                                         base.float_attr.pos_y)
            #print('SCOUT base distance={}, base_range={}'.format(dist, SCOUT_BASE_RANGE))
            if dist < SCOUT_BASE_RANGE:
                self._target.has_enemy_base = True
                self._target.enemy_unit = base
                if len(armys) > 0:
                    self._target.has_army = True
                #print('Scout find base, is_main_base:', dc.dd.scout_pool.has_enemy_main_base())
                if not dc.dd.scout_pool.has_enemy_main_base():
                    #print('SCOUT find base, set main base')
                    self._target.is_main = True
                    if not goback:
                        goback = True
                #print('SCOUT find enemy base, job finish, target=', str(self._target))

        for build in main_base_buildings:
            dist = md.calculate_distance(self._target.pos[0], 
                                         self._target.pos[1],
                                         build.float_attr.pos_x,
                                         build.float_attr.pos_y)
            if dist < SCOUT_BASE_RANGE:
                #print('SCOUT find main_building in main base')
                self._target.has_enemy_base= True
                self._target.is_main = True
                if len(armys) > 0:
                    self._target.has_army = True
                if not goback:
                    goback = True

        for queue in queues:
            dist = md.calculate_distance(self._target.pos[0], 
                                         self._target.pos[1],
                                         queue.float_attr.pos_x,
                                         queue.float_attr.pos_y)
            if dist < SCOUT_BASE_RANGE:
                self._target.has_enemy_base = True
                self._target.has_army = True
                if not dc.dd.scout_pool.has_enemy_main_base():
                    #print('SCOUT find queue, set main base')
                    self._target.is_main = True
                #print('SCOUT find enemy queue, job finish, target=', str(self._target))
                if not goback:
                    goback = True

        for unit in airs:
             dist = md.calculate_distance(self._scout.unit().float_attr.pos_x, 
                                          self._scout.unit().float_attr.pos_y,
                                          unit.float_attr.pos_x,
                                          unit.float_attr.pos_y)
             if dist < SCOUT_SAFE_RANGE:
                 print('SCOUT deteck air unit around me, run')
                 if not goback:
                     goback = True
                 break
        return goback


    def _check_attack(self):
        attack = self._detect_attack()
        if attack:
            if self._status == md.ScoutTaskStatus.DOING:
                #print('SCOUT task turn DOING to UNDER_ATTACK, target=', str(self._target))
                self._status = md.ScoutTaskStatus.UNDER_ATTACK
        else:
            if self._status == md.ScoutTaskStatus.UNDER_ATTACK:
                if self._detect_recovery() and not self._judge_task_done():
                    #print('SCOUT task turn UNDER_ATTACK to DOING, target=', str(self._target))
                    self._status == md.ScoutTaskStatus.DOING
        return attack

    def _check_in_base_range(self):
        dist = md.calculate_distance(self._scout.unit().float_attr.pos_x, 
                                     self._scout.unit().float_attr.pos_y,
                                     self._target.pos[0],
                                     self._target.pos[1])
        if dist < SCOUT_CRUISE_ARRIVAED_RANGE:
            return True
        else:
            return False

    def _check_in_monitor_range(self):
        dist = md.calculate_distance(self._scout.unit().float_attr.pos_x, 
                                     self._scout.unit().float_attr.pos_y,
                                     self._monitor_pos[0],
                                     self._monitor_pos[1])
        if dist < SCOUT_CRUISE_ARRIVAED_RANGE:
            return True
        else:
            return False

    def _judge_task_done(self):
        if self._target.has_enemy_base:
            return True
        elif self._target.has_army:
            return True
        else:
            return False

    def _get_monitor_pos(self):
        avg_pos = self._target.area.calculate_avg()
        diff_x = avg_pos[0] - self._target.pos[0]
        diff_y = avg_pos[1] - self._target.pos[1]
        monitor_pos = (avg_pos[0] + 2.5 * diff_x, avg_pos[1] + 2.5 * diff_y)
        #print('task avg_pos={}, base_pos={} safe_pos={}'.format(
        #      avg_pos, self._target.pos, safe_pos))
        return monitor_pos

class ScoutCruiseTask(ScoutTask):
    def __init__(self, scout, home, target):
        super(ScoutCruiseTask, self).__init__(scout, home)
        self._target = target
        self._paths = []
        self._curr_pos = 0
        self._generate_path()
        self._status = md.ScoutTaskStatus.DOING

    def _do_task_inner(self, view_enemys, dc):
        if self._check_scout_lost():
            self._status = md.ScoutTaskStatus.SCOUT_DESTROY
            return None

        if self._check_attack():
            self._exec_by_status()

        self._detect_enemy(view_enemys, dc)
        return self._exec_by_status()

    def post_process(self):
        self._target.has_cruise = False
        self._scout.is_doing_task = False

    def _exec_by_status(self):
        if self._status == md.ScoutTaskStatus.DOING:
            return self._exec_cruise()
        elif self._status == md.ScoutTaskStatus.DONE:
            return self._move_to_home()
        elif self._status == md.ScoutTaskStatus.UNDER_ATTACK:
            return self._move_to_home()
        else:
            print('SCOUT exec noop, scout status=', self._status)
            return self._noop()

    def _exec_cruise(self):
        if self._curr_pos < 0 or self._curr_pos >= len(self._paths):
            self._curr_pos = 0
        pos = self._paths[self._curr_pos]
        if self._check_arrived_pos(pos):
            self._curr_pos += 1
        return self._move_to_target(pos)

    def _check_arrived_pos(self, pos):
        dist = md.calculate_distance(self._scout.unit().float_attr.pos_x, 
                                     self._scout.unit().float_attr.pos_y,
                                     pos[0], pos[1])
        if dist < SCOUT_CRUISE_ARRIVAED_RANGE:
            return True
        else:
            return False


    def _generate_path(self):
        home_x = self._home[0]
        home_y = self._home[1]
        target_x = self._target.pos[0]
        target_y = self._target.pos[1]

        pos1 = ((home_x * 2) / 3 + target_x / 3, (home_y * 2)/3 + target_y / 3)
        pos2 = ((home_x + target_x)/2, (home_y + target_y)/2)
        pos3 = (pos2[0] - SCOUT_CRUISE_RANGE, pos2[1])
        pos4 = (home_x /3 + (target_x * 2) / 3, home_y / 3 + (target_y * 2) / 3)
        pos5 = (pos2[0] + SCOUT_CRUISE_RANGE, pos2[1])

        self._paths.append(pos1)
        self._paths.append(pos3)
        self._paths.append(pos2)
        self._paths.append(pos4)
        self._paths.append(pos5)

    def _check_attack(self):
        attack = self._detect_attack()
        if attack:
            #print('SCOUT task turn DOING to UNDER_ATTACK, target=', str(self._target))
            self._status = md.ScoutTaskStatus.UNDER_ATTACK

    def _detect_enemy(self, view_enemys, dc):
        spool = dc.dd.scout_pool
        armys = []
        for enemy in view_enemys:
            if enemy.unit_type in md.COMBAT_UNITS:
                armys.append(enemy)

        me = (self._scout.unit().float_attr.pos_x, 
              self._scout.unit().float_attr.pos_y)

        scout_armys = []
        for unit in armys:
            dist = md.calculate_distance(me[0], 
                                         me[1],
                                         unit.float_attr.pos_x,
                                         unit.float_attr.pos_y)
            if dist < SCOUT_CRUISE_RANGE:
                scout_armys.append(unit)
                break
        if len(scout_armys) > 0:
            alarm = sp.ScoutAlarm()
            alarm.enmey_armys = scout_armys
            if not spool.alarms.full():
                spool.alarms.put(alarm)
