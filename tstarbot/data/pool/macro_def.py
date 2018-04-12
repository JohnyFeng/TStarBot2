from enum import Enum, unique
from pysc2.lib.typeenums import RACE, UNIT_TYPEID, ABILITY_ID, UPGRADE_ID, BUFF_ID

@unique
class WorkerState(Enum):
  IDLE = 0
  MINERALS = 1
  GAS = 2
  BUILD = 3
  COMBAT = 4
  MOVE = 5
  SCOUT = 6
  REPAIR = 7
  DEFAULT = 8

@unique
class WorkerSubState(Enum):
  pass

@unique
class AllianceType(Enum):
  SELF = 1
  ALLY = 2
  NEUTRAL = 3
  ENEMY = 4

@unique
class ScoutTaskType(Enum):
  EXPORE = 0
  CRUISE = 1
  SENTINEL = 2
  RETREAT = 3

@unique
class ScoutTaskStatus(Enum):
  INIT = 0
  DOING = 1
  UNDER_ATTACK = 2
  DONE = 3
  SCOUT_DESTROY = 4


WORKER_UNITS = set([UNIT_TYPEID.ZERG_DRONE.value])
BASE_UNITS = set([UNIT_TYPEID.ZERG_HATCHERY.value, UNIT_TYPEID.ZERG_LAIR.value, UNIT_TYPEID.ZERG_HIVE.value])
MINERAL_UNITS = set([UNIT_TYPEID.NEUTRAL_RICHMINERALFIELD.value,
                      UNIT_TYPEID.NEUTRAL_RICHMINERALFIELD750.value, 
                      UNIT_TYPEID.NEUTRAL_MINERALFIELD.value, 
                      UNIT_TYPEID.NEUTRAL_MINERALFIELD750.value,
                      UNIT_TYPEID.NEUTRAL_LABMINERALFIELD.value,
                      UNIT_TYPEID.NEUTRAL_LABMINERALFIELD750.value,
                      UNIT_TYPEID.NEUTRAL_PURIFIERRICHMINERALFIELD.value,
                      UNIT_TYPEID.NEUTRAL_PURIFIERRICHMINERALFIELD750.value,
                      UNIT_TYPEID.NEUTRAL_PURIFIERMINERALFIELD.value,
                      UNIT_TYPEID.NEUTRAL_PURIFIERMINERALFIELD750.value,
                      UNIT_TYPEID.NEUTRAL_BATTLESTATIONMINERALFIELD.value,
                      UNIT_TYPEID.NEUTRAL_BATTLESTATIONMINERALFIELD750.value])

VESPENE_UNITS = set([UNIT_TYPEID.NEUTRAL_VESPENEGEYSER.value,
                     UNIT_TYPEID.NEUTRAL_SPACEPLATFORMGEYSER.value,
                     UNIT_TYPEID.NEUTRAL_RICHVESPENEGEYSER.value])

VESPENE_BUILDING_UNITS = set([UNIT_TYPEID.ZERG_EXTRACTOR.value])

WORKER_RESOURCE_ABILITY = set([ABILITY_ID.HARVEST_GATHER_DRONE.value,
                               ABILITY_ID.HARVEST_RETURN_DRONE.value])

WORKER_BUILD_ABILITY = set([ABILITY_ID.BUILD_HATCHERY.value,
                            ABILITY_ID.BUILD_EVOLUTIONCHAMBER.value,
                            ABILITY_ID.BUILD_EXTRACTOR.value,
                            ABILITY_ID.BUILD_HYDRALISKDEN.value,
                            ABILITY_ID.BUILD_SPAWNINGPOOL.value,
                            ABILITY_ID.BUILD_SPIRE.value,
                            ABILITY_ID.BUILD_ULTRALISKCAVERN.value,
                            ABILITY_ID.BUILD_BANELINGNEST.value,
                            ABILITY_ID.BUILD_INFESTATIONPIT.value,
                            ABILITY_ID.BUILD_NYDUSNETWORK.value,
                            ABILITY_ID.BUILD_ROACHWARREN.value,
                            ABILITY_ID.BUILD_SPINECRAWLER.value,
                            ABILITY_ID.BUILD_SPORECRAWLER.value])

WORKER_MOVE_ABILITY = set([UNIT_TYPEID.ZERG_CHANGELINGZERGLINGWINGS.value,
                           UNIT_TYPEID.ZERG_CHANGELINGZERGLING.value, 
                           UNIT_TYPEID.TERRAN_COMMANDCENTER.value,
                           UNIT_TYPEID.TERRAN_SUPPLYDEPOT.value, 
                           UNIT_TYPEID.TERRAN_REFINERY.value])

WORKER_COMBAT_ABILITY = set([])

BUILDING_UNITS = set([
    # Zerg
    UNIT_TYPEID.ZERG_HATCHERY.value,
    UNIT_TYPEID.ZERG_SPINECRAWLER.value,
    UNIT_TYPEID.ZERG_SPORECRAWLER.value,
    UNIT_TYPEID.ZERG_EXTRACTOR.value,
    UNIT_TYPEID.ZERG_SPAWNINGPOOL.value,
    UNIT_TYPEID.ZERG_EVOLUTIONCHAMBER.value,
    UNIT_TYPEID.ZERG_ROACHWARREN.value,
    UNIT_TYPEID.ZERG_BANELINGNEST.value,
    UNIT_TYPEID.ZERG_CREEPTUMOR.value,
    UNIT_TYPEID.ZERG_LAIR.value,
    UNIT_TYPEID.ZERG_HYDRALISKDEN.value,
    UNIT_TYPEID.ZERG_LURKERDENMP.value,
    UNIT_TYPEID.ZERG_SPIRE.value,
    UNIT_TYPEID.ZERG_SWARMHOSTBURROWEDMP.value,
    UNIT_TYPEID.ZERG_NYDUSNETWORK.value,
    UNIT_TYPEID.ZERG_INFESTATIONPIT.value,
    UNIT_TYPEID.ZERG_HIVE.value,
    UNIT_TYPEID.ZERG_GREATERSPIRE.value,
    UNIT_TYPEID.ZERG_ULTRALISKCAVERN.value,

    # Terran

    # Protoss

])

COMBAT_UNITS = set([
    # Zerg
    UNIT_TYPEID.ZERG_BANELING.value,
    UNIT_TYPEID.ZERG_BANELINGBURROWED.value,
    UNIT_TYPEID.ZERG_BROODLING.value,
    UNIT_TYPEID.ZERG_BROODLORD.value,
    UNIT_TYPEID.ZERG_CHANGELING.value,
    UNIT_TYPEID.ZERG_CHANGELINGMARINE.value,
    UNIT_TYPEID.ZERG_CHANGELINGMARINESHIELD.value,
    UNIT_TYPEID.ZERG_CHANGELINGZEALOT.value,
    UNIT_TYPEID.ZERG_CHANGELINGZERGLING.value,
    UNIT_TYPEID.ZERG_CHANGELINGZERGLINGWINGS.value,
    UNIT_TYPEID.ZERG_CORRUPTOR.value,
    UNIT_TYPEID.ZERG_HYDRALISK.value,
    UNIT_TYPEID.ZERG_HYDRALISKBURROWED.value,
    UNIT_TYPEID.ZERG_INFESTOR.value,
    UNIT_TYPEID.ZERG_INFESTORBURROWED.value,
    UNIT_TYPEID.ZERG_MUTALISK.value,
    UNIT_TYPEID.ZERG_NYDUSCANAL.value,
    UNIT_TYPEID.ZERG_OVERLORD.value,
    UNIT_TYPEID.ZERG_OVERSEER.value,
    UNIT_TYPEID.ZERG_QUEEN.value,
    UNIT_TYPEID.ZERG_QUEENBURROWED.value,
    UNIT_TYPEID.ZERG_RAVAGER.value,
    UNIT_TYPEID.ZERG_ROACH.value,
    UNIT_TYPEID.ZERG_ROACHBURROWED.value,
    UNIT_TYPEID.ZERG_SPINECRAWLER.value,
    UNIT_TYPEID.ZERG_SPINECRAWLERUPROOTED.value,
    UNIT_TYPEID.ZERG_SPORECRAWLER.value,
    UNIT_TYPEID.ZERG_SPORECRAWLERUPROOTED.value,
    UNIT_TYPEID.ZERG_SWARMHOSTMP.value,
    UNIT_TYPEID.ZERG_ULTRALISK.value,
    UNIT_TYPEID.ZERG_ZERGLING.value,
    UNIT_TYPEID.ZERG_ZERGLINGBURROWED.value
])

def calculate_distance(pos_x1, pos_y1, pos_x2, pos_y2):
    x = abs(pos_x1 - pos_x2)
    y = abs(pos_y1 - pos_y2)
    distance = x ** 2 + y ** 2
    return distance ** 0.5

if __name__ == '__main__':
    print(WORKER_UNITS)
    print(BASE_UNITS)
    print(MINERAL_UNITS)
    print(VESPENE_UNITS)
    print(VESPENE_BUILDING_UNITS)
    print(WORKER_RESOURCE_ABILITY)
    print(WORKER_MOVE_ABILITY)
    print(WORKER_BUILD_ABILITY)
    print(WORKER_COMBAT_ABILITY)
