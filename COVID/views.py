# coding:utf-8
from __future__ import unicode_literals

from geopy import Nominatim

from COVID.models import *
from django.db.models import Q
from django.shortcuts import render, redirect
from COVID.point import *
import pandas as pd
import requests
import json
import time, os
import uuid
from math import radians, cos, sin, asin, sqrt

import requests




# Create your views here.


def base(request):
    """"base"""
    return render(request, 'base.html')


def reload():
    """"reload data"""
    longitude = []
    latitude = []
    directory = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
    datas = pd.read_csv(directory + "/data/points18.csv", usecols=['0', '1'])
    current_data = time.strftime("%Y-%m-%d", time.localtime())
    Infected = uuid.uuid4().hex
    for item in datas.values.tolist():
        longitude.append(float(item[1]))
        latitude.append(float(item[0]))
    for index in range(datas.shape[0]):
        point = Point.objects.filter(Q(longitude=longitude[index]) & Q(latitude=latitude[index])).first()
        if point:
            Point.objects.filter(Q(longitude=longitude[index]) & Q(latitude=latitude[index])).update(time=current_data, Infected=Infected)
        else:
            new_point = Point.objects.create(longitude=longitude[index], latitude=latitude[index], time=current_data, Infected=Infected)


def index(request):
    """"index"""
    return render(request, 'index.html')


def distribution(request):
    """"distribution"""
    datas = Point.objects.values_list("longitude", "latitude")
    coordinates = []
    longitude = []
    latitude = []
    point = []
    for data in datas:
        points = []
        separate = list(data)
        points.append(float(separate[0]))
        points.append(float(separate[1]))
        longitude.append(float(separate[0]))
        latitude.append(float(separate[1]))
        coordinates.append(points)
    conversion, discrete ,counts= convex_hull(longitude, latitude)
    for item in conversion:
        point.append(item[0])
    return render(request, 'distribution.html', {'coordinates': coordinates, 'conversion': conversion, 'discrete': discrete, 'point': point, 'counts': counts})

def geocode(address):
    address_uni = address.replace(' ', '')
    if(address_uni.isalpha()):
        lon,lat = geocode_English(address)
    else:
        parameters = {'address': address, 'key': 'be1adc62dd1e55678e4e9361ef751cc1'}
        base = 'http://restapi.amap.com/v3/geocode/geo'
        response = requests.get(base, parameters)
        answer = response.json()
        print(address + " longitude and latitude：", answer['geocodes'][0]['location'])
        lon = float(answer['geocodes'][0]['location'].split(',')[0])
        lat = float(answer['geocodes'][0]['location'].split(',')[1])
    return lon,lat

def geocode_English(address):
    gps = Nominatim(user_agent='myuseragent')
    location = gps.geocode(address, timeout=None)
    lon = location.longitude
    lat = location.latitude
    return lon,lat


def calculate_distance(lon1,lat1,lon2,lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # km
    return c * r * 1000

def avoid_conersion(start,end,conversion):
    if len(conversion) <= 18:
        return conversion

    avoidconersion = []
    dic = {}

    lon_start, lat_start = geocode(start)
    lon_end, lat_end = geocode(end)
    for i in range(len(conversion)):
        distance_start = calculate_distance(lon_start,lat_start,conversion[i][0][0],conversion[i][0][1])
        distance_end = calculate_distance(lon_end,lat_end,conversion[i][0][0],conversion[i][0][1])
        distance = distance_start + distance_end
        dic[i] = distance
    dic_sort = sorted(dic.items(),key= lambda x:x[1])

    for i in range(18):
        if(len(conversion[dic_sort[i][0]])) >= 16:
            avoidconersion.append(conversion[dic_sort[i][0]][:16])
        else:
            avoidconersion.append(conversion[dic_sort[i][0]])
    return avoidconersion


def route(request):
    """"route"""
    if request.method == 'GET':
        datas = Point.objects.values_list("longitude", "latitude")
        longitude = []
        latitude = []
        point = []
        for data in datas:
            separate = list(data)
            longitude.append(float(separate[0]))
            latitude.append(float(separate[1]))
        conversion, discrete,counts = convex_hull(longitude, latitude)
        for item in conversion:
            point.append(item[0])
        location = get_location()
        return render(request, 'route.html', {'conversion': conversion,'discrete': discrete, 'point': point, 'counts': counts, 'location': location})
    elif request.method == "POST":
        post = request.POST
        start = post.get('start')
        end = post.get('end')
        datas = Point.objects.values_list("longitude", "latitude")
        longitude = []
        latitude = []
        point = []
        for data in datas:
            separate = list(data)
            longitude.append(float(separate[0]))
            latitude.append(float(separate[1]))
        conversion, discrete,counts = convex_hull(longitude, latitude)
        for item in conversion:
            point.append(item[0])
        location = get_location()
        for i in conversion:
            print(len(i))
        print("conversion的个数",len(conversion))
        avoidconversion = avoid_conersion(start,end,conversion)
        return render(request, 'route_show.html', {'start': start, 'end': end, 'avoidconversion':avoidconversion,'conversion': conversion, 'discrete': discrete,'point': point, 'counts': counts, 'location': location})


def add_points(request):
    """"add risk point"""
    if request.method == 'GET':
        return render(request, 'add_points.html')
    elif request.method == "POST":
        message = "Information Entry Failure!"
        current_data = time.strftime("%Y-%m-%d", time.localtime())
        post = request.POST
        longitude = post.get('longitude')
        latitude = post.get('latitude')
        date = post.get('date')
        Infected = uuid.uuid4().hex
        if date:
            current_data = date
        place = post.get('place')
        point = Point.objects.filter(Q(longitude=longitude) & Q(latitude=latitude)).first()
        if point:
            Point.objects.filter(Q(longitude=longitude) & Q(latitude=latitude)).update(time=current_data, place=place, Infected=Infected)
            message = "Information Entry Successful!"
        else:
            new_point = Point.objects.create(longitude=longitude, latitude=latitude, time=current_data, place=place, Infected=Infected)
            message = "Information Entry Successful!"
        return render(request, 'add_points.html', {'message': message})


def infected_points(request):
    """"add risk point(infected)"""
    if request.method == 'GET':
        return render(request, 'infected_points.html')
    elif request.method == "POST":
        message = "Information Entry Failure!"
        current_data = time.strftime("%Y-%m-%d", time.localtime())
        post = request.POST
        date = post.get('date')
        lnglat = post.get('lnglat')
        lnglat_list = lnglat.split(',')
        longitude = float(lnglat_list[0])
        latitude = float(lnglat_list[1])
        print(lnglat,"lnglat")

        Infected = uuid.uuid4().hex
        if date:
            current_data = date
        place = post.get('place')
        point = Point.objects.filter(Q(longitude=longitude) & Q(latitude=latitude)).first()
        if point:
            Point.objects.filter(Q(longitude=longitude) & Q(latitude=latitude)).update(time=current_data, place=place, Infected=Infected)
            message = "Information Entry Successful!"
        else:
            new_point = Point.objects.create(longitude=longitude, latitude=latitude, time=current_data, place=place, Infected=Infected)
            message = "Information Entry Successful!"

        # point = Risk.objects.filter(Q(longitude=longitude) & Q(latitude=latitude)).first()
        # if point:
        #     Risk.objects.filter(Q(longitude=longitude) & Q(latitude=latitude)).update(time=current_data, place=place,
        #                                                                                Infected=Infected)
        #     message = "Information Entry Successful!"
        # else:
        #     new_point = Risk.objects.create(longitude=longitude, latitude=latitude, time=current_data, place=place,
        #                                      Infected=Infected)
        #     message = "Information Entry Successful!"
        return render(request, 'infected_points.html', {'message': message})




def get_location():
    """"get location information, only valid in China, otherwise it will error"""
    location = 'Tongji University'  # Default location
    # Get current location, latitude and longitude coordinates
    coordinates_response = requests.request("POST", 'http://restapi.amap.com/v3/ip?key=be1adc62dd1e55678e4e9361ef751cc1')
    coordinates_result = json.loads(coordinates_response.text)
    if coordinates_result['status'] == '1':
        coordinates = coordinates_result['rectangle']
        strlist = coordinates.split(';')
        url = 'https://restapi.amap.com/v3/geocode/regeo?location={}&key=be1adc62dd1e55678e4e9361ef751cc1'.format(strlist[0])
        location_response = requests.request("POST", url)
        location_result = json.loads(location_response.text)
        if location_result['status'] == '1':
            address = location_result['regeocode']['formatted_address']
            print("current loaction:", address)
            if address.startswith('上海', 0, 2):
                location = address
    print("location:", location)
    return location
# reload()