from django.shortcuts import render
from django.http import HttpResponse, HttpRequest


def welcome(reauest: HttpRequest):
    return HttpResponse("Hello World!")
