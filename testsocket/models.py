from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

# Create your models here.
def get_default_inventory():
    return [[0,0]]

class User(AbstractUser):
    health = models.IntegerField(default=100)
    maxHealth = models.IntegerField(default=100)
    energy = models.IntegerField(default=100)
    maxEnergy = models.IntegerField(default=100)
    inventory = ArrayField(
        ArrayField(
            models.IntegerField()
        ), default = get_default_inventory
    )
    gold = models.IntegerField(default=0)
    maxInventorySpace = models.IntegerField(default=64)
    weapon = models.IntegerField(default=0)
    armor = models.IntegerField(default=0)
    pickaxe = models.IntegerField(default=0)
    shovel = models.IntegerField(default=0)
    hoe = models.IntegerField(default=0)
    miningSkill = models.IntegerField(default=0)
    miningExp = models.IntegerField(default=0)
    gatheringSkill = models.IntegerField(default=0)
    gatheringExp = models.IntegerField(default=0)
    loggingSkill = models.IntegerField(default=0)
    loggingExp = models.IntegerField(default=0)
    fishingSkill = models.IntegerField(default=0)
    fishingExp = models.IntegerField(default=0)
    breedingSkill = models.IntegerField(default=0)
    breedingExp = models.IntegerField(default=0)
    catchingSkill = models.IntegerField(default=0)
    catchingExp = models.IntegerField(default=0)
    posX = models.IntegerField(default=700)
    posY = models.IntegerField(default=700)
    posMap = models.CharField(max_length=50, default="map")
    posDirection = models.CharField(max_length=10, default="up")
    sprite = models.IntegerField(default=1)
    itemInHand = models.CharField(max_length=10,default="weapon")