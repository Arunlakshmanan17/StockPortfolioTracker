import yfinance as yf

from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .models import StockHolding


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is not None:

            authenticated_user = authenticate(
                request,
                username=user.username,
                password=password
            )

            if authenticated_user is not None:

                login(request, authenticated_user)

                return redirect("dashboard")

        messages.error(
            request,
            "Invalid email or password."
        )

        return redirect("login")

    return render(
        request,
        "login.html"
    )


# =========================================================
# REGISTER
# =========================================================

def register_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        # -------------------------------------------------
        # PASSWORD CHECK
        # -------------------------------------------------

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("register")

        # -------------------------------------------------
        # USERNAME CHECK
        # -------------------------------------------------

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("register")

        # -------------------------------------------------
        # EMAIL CHECK
        # -------------------------------------------------

        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "Email already registered."
            )

            return redirect("register")

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(
            request,
            "Account created successfully. Please login."
        )

        return redirect("login")

    return render(
        request,
        "register.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@login_required(login_url="login")
def dashboard_view(request):

    # -----------------------------------------------------
    # GET ONLY CURRENT USER'S STOCKS
    # -----------------------------------------------------

    stocks = StockHolding.objects.filter(
        user=request.user
    )

    # -----------------------------------------------------
    # TOTAL INVESTMENT
    # -----------------------------------------------------

    total_investment = sum(
        (
            stock.investment_value()
            for stock in stocks
        ),
        Decimal("0.00")
    )

    # -----------------------------------------------------
    # CURRENT PORTFOLIO VALUE
    # -----------------------------------------------------

    portfolio_value = sum(
        (
            stock.current_value()
            for stock in stocks
        ),
        Decimal("0.00")
    )

    # -----------------------------------------------------
    # PROFIT / LOSS
    # -----------------------------------------------------

    profit_loss = (
        portfolio_value
        - total_investment
    )

    # -----------------------------------------------------
    # NUMBER OF STOCKS
    # -----------------------------------------------------

    stock_count = stocks.count()

    # =====================================================
    # CHART DATA
    # =====================================================

    chart_data = []

    for stock in stocks:

        chart_data.append({

            "symbol": stock.symbol,

            "current_value": float(
                stock.current_value()
            ),

            "profit_loss": float(
                stock.profit_loss()
            )

        })

    # -----------------------------------------------------
    # CONTEXT
    # -----------------------------------------------------

    context = {

        "stocks": stocks,

        "total_investment":
            total_investment,

        "portfolio_value":
            portfolio_value,

        "profit_loss":
            profit_loss,

        "stock_count":
            stock_count,

        "chart_data":
            chart_data,
    }

    return render(
        request,
        "dashboard.html",
        context
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("login")


# =========================================================
# ADD STOCK
# =========================================================

@login_required(login_url="login")
def add_stock_view(request):

    if request.method == "POST":

        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        symbol = request.POST.get(
            "symbol",
            ""
        ).strip().upper()

        company_name = request.POST.get(
            "company_name",
            ""
        ).strip()

        quantity = request.POST.get(
            "quantity",
            ""
        ).strip()

        purchase_price = request.POST.get(
            "purchase_price",
            ""
        ).strip()

        # -------------------------------------------------
        # REQUIRED FIELD CHECK
        # -------------------------------------------------

        if not symbol:

            messages.error(
                request,
                "Please enter the stock symbol."
            )

            return redirect("add_stock")

        if not company_name:

            messages.error(
                request,
                "Please enter the company name."
            )

            return redirect("add_stock")

        if not quantity:

            messages.error(
                request,
                "Please enter the quantity."
            )

            return redirect("add_stock")

        if not purchase_price:

            messages.error(
                request,
                "Please enter the purchase price."
            )

            return redirect("add_stock")

        # -------------------------------------------------
        # CONVERT QUANTITY
        # -------------------------------------------------

        try:

            quantity = int(quantity)

        except ValueError:

            messages.error(
                request,
                "Quantity must be a valid number."
            )

            return redirect("add_stock")

        # -------------------------------------------------
        # CONVERT PURCHASE PRICE
        # -------------------------------------------------

        try:

            purchase_price = Decimal(
                purchase_price
            )

        except InvalidOperation:

            messages.error(
                request,
                "Purchase price must be a valid number."
            )

            return redirect("add_stock")

        # -------------------------------------------------
        # VALIDATE VALUES
        # -------------------------------------------------

        if quantity <= 0:

            messages.error(
                request,
                "Quantity must be greater than zero."
            )

            return redirect("add_stock")

        if purchase_price <= 0:

            messages.error(
                request,
                "Purchase price must be greater than zero."
            )

            return redirect("add_stock")

        # =================================================
        # FETCH LIVE PRICE FROM YAHOO FINANCE
        # =================================================

        try:

            # Indian NSE stocks
            yahoo_symbol = symbol + ".NS"

            print(
                "========================================"
            )

            print(
                "Fetching live price for:",
                yahoo_symbol
            )

            ticker = yf.Ticker(
                yahoo_symbol
            )

            data = ticker.history(
                period="1d"
            )

            # -------------------------------------------------
            # CHECK PRICE DATA
            # -------------------------------------------------

            if data.empty:

                messages.error(
                    request,
                    f"Could not find live price for {symbol}. "
                    f"Please check the NSE stock symbol."
                )

                return redirect("add_stock")

            # -------------------------------------------------
            # GET LATEST PRICE
            # -------------------------------------------------

            latest_price = data[
                "Close"
            ].iloc[-1]

            current_price = Decimal(
                str(
                    round(
                        float(latest_price),
                        2
                    )
                )
            )

            print(
                "Live price:",
                current_price
            )

            print(
                "========================================"
            )

        except Exception as e:

            print(
                "YFinance Error:",
                e
            )

            messages.error(
                request,
                f"Unable to fetch live price for {symbol}. "
                f"Please try again."
            )

            return redirect("add_stock")

        # -------------------------------------------------
        # VALIDATE LIVE PRICE
        # -------------------------------------------------

        if current_price <= 0:

            messages.error(
                request,
                "Invalid market price received."
            )

            return redirect("add_stock")

        # =================================================
        # SAVE STOCK
        # =================================================

        try:

            stock = StockHolding.objects.create(

                user=request.user,

                symbol=symbol,

                company_name=company_name,

                quantity=quantity,

                purchase_price=purchase_price,

                current_price=current_price
            )

            print(
                "========================================"
            )

            print(
                "STOCK ADDED SUCCESSFULLY"
            )

            print(
                "Stock ID:",
                stock.id
            )

            print(
                "Symbol:",
                stock.symbol
            )

            print(
                "Quantity:",
                stock.quantity
            )

            print(
                "Purchase Price:",
                stock.purchase_price
            )

            print(
                "Current Price:",
                stock.current_price
            )

            print(
                "========================================"
            )

        except Exception as e:

            print(
                "DATABASE ERROR:",
                e
            )

            messages.error(
                request,
                "Unable to save the stock."
            )

            return redirect("add_stock")

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        messages.success(
            request,
            f"{symbol} added successfully! "
            f"Current price: ₹{current_price}"
        )

        return redirect("dashboard")

    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "add_stock.html"
    )


# =========================================================
# REFRESH STOCK PRICES
# =========================================================

@login_required(login_url="login")
def refresh_prices_view(request):

    # -----------------------------------------------------
    # GET CURRENT USER'S STOCKS
    # -----------------------------------------------------

    stocks = StockHolding.objects.filter(
        user=request.user
    )

    updated_count = 0

    failed_stocks = []

    # -----------------------------------------------------
    # UPDATE EACH STOCK
    # -----------------------------------------------------

    for stock in stocks:

        try:

            symbol = stock.symbol.upper()

            # -------------------------------------------------
            # CREATE YAHOO SYMBOL
            # -------------------------------------------------

            if "." not in symbol:

                yahoo_symbol = symbol + ".NS"

            else:

                yahoo_symbol = symbol

            print(
                f"Updating {symbol} using {yahoo_symbol}"
            )

            # -------------------------------------------------
            # FETCH YAHOO FINANCE DATA
            # -------------------------------------------------

            ticker = yf.Ticker(
                yahoo_symbol
            )

            data = ticker.history(
                period="1d"
            )

            # -------------------------------------------------
            # CHECK DATA
            # -------------------------------------------------

            if data.empty:

                failed_stocks.append(
                    stock.symbol
                )

                continue

            # -------------------------------------------------
            # GET LATEST PRICE
            # -------------------------------------------------

            latest_price = data[
                "Close"
            ].iloc[-1]

            # -------------------------------------------------
            # UPDATE DATABASE
            # -------------------------------------------------

            stock.current_price = Decimal(
                str(
                    round(
                        float(latest_price),
                        2
                    )
                )
            )

            stock.save(
                update_fields=[
                    "current_price"
                ]
            )

            updated_count += 1

        except Exception as e:

            print(
                f"Error updating {stock.symbol}: {e}"
            )

            failed_stocks.append(
                stock.symbol
            )

    # -----------------------------------------------------
    # SUCCESS MESSAGE
    # -----------------------------------------------------

    if updated_count > 0:

        messages.success(
            request,
            f"Updated prices for "
            f"{updated_count} stock(s) successfully."
        )

    # -----------------------------------------------------
    # FAILED STOCKS
    # -----------------------------------------------------

    if failed_stocks:

        messages.warning(
            request,
            "Could not update: "
            + ", ".join(failed_stocks)
        )

    # -----------------------------------------------------
    # NO STOCKS
    # -----------------------------------------------------

    if (
        updated_count == 0
        and not failed_stocks
    ):

        messages.info(
            request,
            "Your portfolio has no stocks to update."
        )

    return redirect("dashboard")


# =========================================================
# EDIT STOCK
# =========================================================

@login_required(login_url="login")
def edit_stock_view(request, stock_id):

    # -----------------------------------------------------
    # GET USER'S STOCK
    # -----------------------------------------------------

    try:

        stock = StockHolding.objects.get(
            id=stock_id,
            user=request.user
        )

    except StockHolding.DoesNotExist:

        messages.error(
            request,
            "Stock not found."
        )

        return redirect("dashboard")

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        symbol = request.POST.get(
            "symbol",
            ""
        ).strip().upper()

        company_name = request.POST.get(
            "company_name",
            ""
        ).strip()

        quantity = request.POST.get(
            "quantity",
            ""
        ).strip()

        purchase_price = request.POST.get(
            "purchase_price",
            ""
        ).strip()

        current_price = request.POST.get(
            "current_price",
            ""
        ).strip()

        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not symbol or not company_name:

            messages.error(
                request,
                "Please enter symbol and company name."
            )

            return redirect(
                "edit_stock",
                stock_id=stock.id
            )

        # -------------------------------------------------
        # CONVERT NUMBERS
        # -------------------------------------------------

        try:

            quantity = int(quantity)

            purchase_price = Decimal(
                purchase_price
            )

            current_price = Decimal(
                current_price
            )

        except (
            ValueError,
            InvalidOperation
        ):

            messages.error(
                request,
                "Please enter valid numbers."
            )

            return redirect(
                "edit_stock",
                stock_id=stock.id
            )

        # -------------------------------------------------
        # VALIDATE
        # -------------------------------------------------

        if quantity <= 0:

            messages.error(
                request,
                "Quantity must be greater than zero."
            )

            return redirect(
                "edit_stock",
                stock_id=stock.id
            )

        if purchase_price <= 0:

            messages.error(
                request,
                "Purchase price must be greater than zero."
            )

            return redirect(
                "edit_stock",
                stock_id=stock.id
            )

        if current_price <= 0:

            messages.error(
                request,
                "Current price must be greater than zero."
            )

            return redirect(
                "edit_stock",
                stock_id=stock.id
            )

        # -------------------------------------------------
        # UPDATE STOCK
        # -------------------------------------------------

        stock.symbol = symbol

        stock.company_name = company_name

        stock.quantity = quantity

        stock.purchase_price = purchase_price

        stock.current_price = current_price

        stock.save()

        messages.success(
            request,
            f"{symbol} updated successfully."
        )

        return redirect("dashboard")

    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "edit_stock.html",
        {
            "stock": stock
        }
    )


# =========================================================
# DELETE STOCK
# =========================================================

@login_required(login_url="login")
def delete_stock_view(request, stock_id):

    # -----------------------------------------------------
    # GET USER'S STOCK
    # -----------------------------------------------------

    try:

        stock = StockHolding.objects.get(
            id=stock_id,
            user=request.user
        )

    except StockHolding.DoesNotExist:

        messages.error(
            request,
            "Stock not found."
        )

        return redirect("dashboard")

    # =====================================================
    # DELETE
    # =====================================================

    if request.method == "POST":

        symbol = stock.symbol

        stock.delete()

        messages.success(
            request,
            f"{symbol} deleted successfully."
        )

        return redirect("dashboard")

    # =====================================================
    # CONFIRMATION PAGE
    # =====================================================

    return render(
        request,
        "delete_stock.html",
        {
            "stock": stock
        }
    )