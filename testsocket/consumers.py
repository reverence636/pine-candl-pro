import asyncio
import json
import math
import os
import threading
import time

import django
from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model


class PracticeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # noinspection PyAttributeOutsideInit
        self.user = self.scope["user"]
        # noinspection PyAttributeOutsideInit
        self.alive = True
        # noinspection PyAttributeOutsideInit
        self.roomGroupName = "client_group"
        await self.accept()
        if self.user.posMap == "map":
            self.user.posMap = "STARTING_MAP"

        await self.channel_layer.group_add(self.roomGroupName, self.channel_name)
        await self.channel_layer.send("worker_group", {"type": "log_event", "p": "player",
                                                       "d": {"name": str(self.user), "id": int(self.user.id),
                                                             "channel": self.channel_name, "health": self.user.health,
                                                             "maxHealth": self.user.maxHealth,
                                                             "energy": self.user.energy,
                                                             "maxEnergy": self.user.maxEnergy,
                                                             "inventory": self.user.inventory, "gold": self.user.gold,
                                                             "equippedItems": {"weapon": self.user.weapon,
                                                                               "armor": self.user.armor,
                                                                               "pickaxe": self.user.pickaxe,
                                                                               "shovel": self.user.shovel,
                                                                               "hoe": self.user.hoe},
                                                             "maxInventorySpace": self.user.maxInventorySpace,
                                                             "itemInHand": self.user.itemInHand, "skills": {
                                                               "breeding": {"level": self.user.breedingSkill,
                                                                            "exp": self.user.breedingExp},
                                                               "catching": {"level": self.user.catchingSkill,
                                                                            "exp": self.user.catchingExp},
                                                               "fishing": {"level": self.user.fishingSkill,
                                                                           "exp": self.user.fishingExp},
                                                               "gathering": {"level": self.user.gatheringSkill,
                                                                             "exp": self.user.gatheringExp},
                                                               "logging": {"level": self.user.loggingSkill,
                                                                           "exp": self.user.loggingExp},
                                                               "mining": {"level": self.user.miningSkill,
                                                                          "exp": self.user.miningExp}},
                                                             "position": {"x": self.user.posX, "y": self.user.posY,
                                                                          "direction": self.user.posDirection,
                                                                          "map": self.user.posMap},
                                                             "sprite": self.user.sprite}, "id": int(self.user.id)})

    async def disconnect(self, close_code):
        await self.channel_layer.send("worker_group", {"type": "log_event", "p": "disconnect", "d": self.channel_name,
                                                       "id": int(self.user.id)})
        await self.channel_layer.group_discard(self.roomGroupName, self.channel_name)
        self.alive = False

    # noinspection PyMethodOverriding
    async def receive(self, text_data):
        jdata = json.loads(text_data)
        await self.channel_layer.send("worker_group",
                                      {"type": "log_event", "p": jdata["p"], "d": jdata["d"], "id": int(self.user.id)})

    # Server sends message
    async def sendMessage(self, packet):
        await self.send(text_data=json.dumps(packet))


class PracticeWorker(AsyncConsumer):

    @staticmethod
    def save_player_data():
        User = get_user_model()
        counter = 0
        while True:
            time.sleep(.05)
            counter += 1
            if counter == 80:
                counter = 0
                with open("./testsocket/players.json", "r") as json_file:
                    json_obj = json.load(json_file)
                    if json_obj:
                        for player in json_obj:
                            user = User.objects.get(id=player)
                            user.health = json_obj[player]["health"]
                            user.maxHealth = json_obj[player]["maxHealth"]
                            user.energy = json_obj[player]["energy"]
                            user.maxEnergy = json_obj[player]["maxEnergy"]
                            user.inventory = json_obj[player]["inventory"]
                            user.gold = json_obj[player]["gold"]
                            user.maxInventorySpace = json_obj[player]["maxInventorySpace"]
                            user.weapon = json_obj[player]["equippedItems"]["weapon"]
                            user.armor = json_obj[player]["equippedItems"]["armor"]
                            user.pickaxe = json_obj[player]["equippedItems"]["pickaxe"]
                            user.shovel = json_obj[player]["equippedItems"]["shovel"]
                            user.hoe = json_obj[player]["equippedItems"]["hoe"]

                            user.miningSkill = json_obj[player]["skills"]["mining"]["level"]
                            user.miningExp = json_obj[player]["skills"]["mining"]["exp"]
                            user.gatheringSkill = json_obj[player]["skills"]["gathering"]["level"]
                            user.gatheringExp = json_obj[player]["skills"]["gathering"]["exp"]
                            user.loggingSkill = json_obj[player]["skills"]["logging"]["level"]
                            user.loggingExp = json_obj[player]["skills"]["logging"]["exp"]
                            user.fishingSkill = json_obj[player]["skills"]["fishing"]["level"]
                            user.fishingExp = json_obj[player]["skills"]["fishing"]["exp"]
                            user.breedingSkill = json_obj[player]["skills"]["breeding"]["level"]
                            user.breedingExp = json_obj[player]["skills"]["breeding"]["exp"]
                            user.catchingSkill = json_obj[player]["skills"]["catching"]["level"]
                            user.catchingExp = json_obj[player]["skills"]["catching"]["exp"]
                            user.posX = json_obj[player]["position"]["x"]
                            user.posY = json_obj[player]["position"]["y"]
                            user.itemInHand = json_obj[player]["itemInHand"]
                            if (json_obj[player]["position"]["map"] is None) or (
                                    json_obj[player]["position"]["map"] == "map"):
                                user.posMap = "STARTING_MAP"
                            else:
                                user.posMap = json_obj[player]["position"]["map"]
                            user.posDirection = json_obj[player]["position"]["direction"]
                            user.sprite = json_obj[player]["sprite"]
                            user.save()

    @staticmethod
    def write_players_to_file(players):
        with open("./testsocket/players.json", "w") as json_file:
            json_obj = json.dumps(players)
            json_file.write(json_obj)

    def __init__(self):
        super().__init__()
        self.started_loop = True
        loop = asyncio.get_event_loop()
        future = asyncio.run_coroutine_threadsafe(self.start_loop(), loop)
        saving_thread = threading.Thread(target=self.save_player_data, daemon=True)
        saving_thread.start()
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectpine.settings")
        django.setup()
        self.hour_of_day = 0.0
        self.players = {}
        self.events = {}
        self.maps = {}
        for filename in os.listdir("./testsocket/maps/"):
            filepath = os.path.join("./testsocket/maps/", filename)
            if os.path.isfile(filepath):  # Ensure it's a file, not a subdirectory
                with open(filepath, 'r') as file:
                    map = json.load(file)
                    self.maps[filepath.split("/")[-1].split(".")[0]] = map

    async def send_init_packet(self, player_packet):
        current_map_name = player_packet["position"]["map"]
        print(current_map_name)
        map_data = self.maps[current_map_name]
        channel = player_packet["channel"]
        player_list = [x for x in self.players.values() if x["position"]["map"] == current_map_name]
        await self.channel_layer.send(channel, {"type": "sendMessage", "p": "init_packet",
                                                "d": {"map": map_data, "players": player_list,
                                                      "time": self.hour_of_day}})
        await self.channel_layer.send(channel, {"type": "sendMessage", "p": "self", "d": player_packet})
        await self.channel_layer.group_send(current_map_name,
                                            {"type": "sendMessage", "p": "player", "d": player_packet})
        await self.channel_layer.group_add(current_map_name, channel)
        print(player_packet["position"]["map"])

    async def broadcast_player_disconnect(self, player_id):
        current_map_name = self.players[player_id]["position"]["map"]
        channel = self.players[player_id]["channel"]
        await self.channel_layer.group_send(current_map_name,
                                            {"type": "sendMessage", "p": "disconnect", "d": player_id})
        await self.channel_layer.group_discard(current_map_name, channel)

    async def send_chat(self, sender, chat_packet):
        match chat_packet["destination"]:
            case "map":
                current_map_name = self.players[sender]["position"]["map"]
                await self.channel_layer.group_send(current_map_name, {"type": "sendMessage", "p": "chat",
                                                                       "d": {"sender": sender,
                                                                             "message": chat_packet["message"]}})

            case int():
                channel = self.players[chat_packet["destination"]]["channel"]
                await self.channel_layer.send(channel, {"type": "sendMessage", "p": "chat",
                                                        "d": {"sender": sender, "message": chat_packet["message"]}})

            case _:
                print("Unknown destination")

    async def set_sprite(self, player_id, sprite_id):
        current_map_name = self.players[player_id]["position"]["map"]
        self.players[player_id]["sprite"] = sprite_id
        await self.channel_layer.group_send(current_map_name, {"type": "sendMessage", "p": "setsprite",
                                                               "d": {"player": player_id, "sprite": sprite_id}})

    async def start_loop(self):
        player_write_counter = 0
        time_of_day_counter = 0
        while True:
            await asyncio.sleep(.05)
            player_write_counter += 1
            time_of_day_counter += 1
            if player_write_counter == 40:
                self.write_players_to_file(self.players)
                player_write_counter = 0
            if time_of_day_counter == 300:
                self.hour_of_day += 0.25
                if self.hour_of_day == 24:
                    self.hour_of_day = 0
                await self.channel_layer.group_send("client_group",
                                                    {"type": "sendMessage", "p": "time", "d": self.hour_of_day})
                time_of_day_counter = 0
            for player in self.events:
                for event in self.events[player]:
                    match event:

                        # player packet received only from the websocket on join
                        case "player":
                            print("player")
                            if self.events[player][event]["id"] not in self.players.keys():
                                await self.send_init_packet(self.events[player][event])
                                self.players[player] = self.events[player][event]
                            else:
                                print("player already joined")

                        # input d: [x, y, direction, map]
                        # output d: {id: integer, x: integer, y: integer, direction: string, map: string}
                        case "position":
                            print("position")
                            data = {"id": int(player), "x": self.events[player][event][0],
                                    "y": self.events[player][event][1], "direction": self.events[player][event][2],
                                    "map": self.players[player]["position"]["map"]}
                            await self.channel_layer.group_send(self.players[player]["position"]["map"],
                                                                {"type": "sendMessage", "p": event, "d": data})
                            del data["id"]
                            self.players[player]["position"] = data

                        # input d: None
                        case "rightClick":
                            print("rightClick")
                            x = self.players[player]["position"]["x"]
                            y = self.players[player]["position"]["y"]
                            direction = self.players[player]["position"]["direction"]
                            map = self.maps[self.players[player]["position"]["map"]]
                            current_tool = self.players[player][self.players[player]["itemInHand"]]

                        # input d: None
                        case "leftClick":
                            print("leftClick")
                            x = self.players[player]["position"]["x"]
                            y = self.players[player]["position"]["y"]
                            direction = self.players[player]["position"]["direction"]
                            map = self.maps[self.players[player]["position"]["map"]]
                            current_tool = self.players[player][self.players[player]["itemInHand"]]

                        # input d: integer
                        case "slotChange":
                            print("slotChange")
                            self.players[player]["itemInHand"] = self.events[player][event]

                        # disconnect is received only from the websocket on disconnect, broadcasts an integer for output
                        case "disconnect":
                            print("disconnect")
                            if player in self.players:
                                if self.events[player][event] == self.players[player]["channel"]:
                                    await self.broadcast_player_disconnect(player)
                                    del self.players[player]
                                else:
                                    print("this player isn't connected")
                            else:
                                print("You aren't in the game yet")

                        # input d: {destination: object, message: string} destination should be "map" or an integer
                        # output d: {sender: integer, message: string}
                        case "chat":
                            await self.send_chat(player, self.events[player][event])

                        # input d: integer
                        # output d: {player: integer, sprite: integer}
                        case "setsprite":
                            await self.set_sprite(player, self.events[player][event])

                        case "teleport":
                            portal_name = self.events[player][event]
                            portal = [x for x in
                                      [x for x in self.maps[self.players[player]["position"]["map"]]["layers"] if
                                       x["name"] == "Portals"][0]["objects"] if x["name"] == portal_name][0]
                            portal_pos = (portal["x"], portal["y"])
                            player_pos = (self.players[player]["position"]["x"], self.players[player]["position"]["y"])
                            distance = math.dist(portal_pos, player_pos)
                            if distance < 20:
                                for x in portal["properties"]:
                                    match x["name"]:
                                        case "dest_map":
                                            dest_map = x["value"]
                                        case "dest_x":
                                            dest_x = x["value"]
                                        case "dest_y":
                                            dest_y = x["value"]
                                await self.channel_layer.group_discard(self.players[player]["position"]["map"], self.players[player]["channel"])
                                await self.broadcast_player_disconnect(player)
                                self.players[player]["position"]["map"]=dest_map
                                self.players[player]["position"]["x"]=dest_x
                                self.players[player]["position"]["y"]=dest_y
                                print("Map", dest_map)
                                print(self.players[player]["position"]["map"])
                                await self.send_init_packet(self.players[player])
                                print(self.players[player]["position"]["map"])
                                self.events[player] = {}
                        case _:
                            print("Received unknown packet", event)

                self.events[player] = {}

    async def log_event(self, packet):
        uid = packet["id"]
        p_type = packet["p"]
        data = packet["d"]
        if uid not in self.events:
            self.events[uid] = {}
        self.events[uid][p_type] = data
