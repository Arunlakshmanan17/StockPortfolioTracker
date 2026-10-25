"""
URL configuration for stocktracker project.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from stocks.views import (
    login_view,
    register_view,
    dashboard_view,
    logout_view,
    add_stock_view,
    refresh_prices_view,
    edit_stock_view,
    delete_stock_view,
)


urlpatterns = [

    # =========================
    # ADMIN
    # =========================

    path(
        "admin/",
        admin.site.urls
    ),


    # =========================
    # LOGIN
    # =========================

    path(
        "login/",
        login_view,
        name="login"
    ),


    # =========================
    # REGISTER
    # =========================

    path(
        "register/",
        register_view,
        name="register"
    ),


    # =========================
    # DASHBOARD
    # =========================

    path(
        "dashboard/",
        dashboard_view,
        name="dashboard"
    ),


    # =========================
    # ADD STOCK
    # =========================

    path(
        "add-stock/",
        add_stock_view,
        name="add_stock"
    ),


    # =========================
    # LOGOUT
    # =========================

    path(
        "logout/",
        logout_view,
        name="logout"
    ),


    # =========================
    # REFRESH STOCK PRICES
    # =========================

    path(
        "refresh-prices/",
        refresh_prices_view,
        name="refresh_prices"
    ),


    # =========================
    # EDIT STOCK
    # =========================

    path(
        "edit-stock/<int:stock_id>/",
        edit_stock_view,
        name="edit_stock"
    ),


    # =========================
    # DELETE STOCK
    # =========================

    path(
        "delete-stock/<int:stock_id>/",
        delete_stock_view,
        name="delete_stock"
    ),

    path(
    "",
    RedirectView.as_view(
        pattern_name="login",
        permanent=False
    ),
),

]