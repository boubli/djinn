"""
Stripe Plugin for DJINN
Stripe payments management.
"""
import click
from rich.console import Console
from rich.table import Table
import os
import json
from pathlib import Path

console = Console()

PLUGIN_NAME = "stripe"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Stripe payments and billing management."

CONFIG_FILE = Path.home() / ".djinn" / "stripe.json"


def get_stripe_client():
    """Get Stripe client."""
    try:
        import stripe
        
        api_key = os.environ.get("STRIPE_API_KEY")
        if not api_key:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE) as f:
                    api_key = json.load(f).get("api_key")
        
        if not api_key:
            console.print("[error]STRIPE_API_KEY not set[/error]")
            console.print("[muted]Run: djinn stripe auth YOUR_SECRET_KEY[/muted]")
            return None
        
        stripe.api_key = api_key
        return stripe
    except ImportError:
        console.print("[error]stripe not installed. Run: pip install stripe[/error]")
        return None


@click.group()
def stripe_cli():
    """Stripe commands."""
    pass


@stripe_cli.command(name="auth")
@click.argument("api_key")
def set_auth(api_key):
    """Save Stripe API key."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"api_key": api_key}, f)
    
    console.print("[success]✓ Stripe API key saved![/success]")


@stripe_cli.command(name="balance")
def get_balance():
    """Get account balance."""
    stripe = get_stripe_client()
    if not stripe:
        return
    
    try:
        balance = stripe.Balance.retrieve()
        
        console.print("\n[bold cyan]💳 Stripe Balance[/bold cyan]\n")
        
        for bal in balance.available:
            amount = bal.amount / 100
            console.print(f"[success]Available: {bal.currency.upper()} {amount:,.2f}[/success]")
        
        for bal in balance.pending:
            amount = bal.amount / 100
            console.print(f"[muted]Pending: {bal.currency.upper()} {amount:,.2f}[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@stripe_cli.command(name="customers")
@click.option("--limit", default=20, type=int)
def list_customers(limit):
    """List customers."""
    stripe = get_stripe_client()
    if not stripe:
        return
    
    try:
        customers = stripe.Customer.list(limit=limit)
        
        console.print("\n[bold cyan]👥 Customers[/bold cyan]\n")
        
        table = Table()
        table.add_column("Email", style="cyan")
        table.add_column("Name")
        table.add_column("Created")
        table.add_column("ID")
        
        for customer in customers.data:
            from datetime import datetime
            created = datetime.fromtimestamp(customer.created).strftime("%Y-%m-%d")
            
            table.add_row(
                customer.email or "-",
                customer.name or "-",
                created,
                customer.id[:20] + "..."
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@stripe_cli.command(name="payments")
@click.option("--limit", default=20, type=int)
@click.option("--status", type=click.Choice(["succeeded", "pending", "failed"]))
def list_payments(limit, status):
    """List payment intents."""
    stripe = get_stripe_client()
    if not stripe:
        return
    
    try:
        params = {"limit": limit}
        
        payments = stripe.PaymentIntent.list(**params)
        
        console.print("\n[bold cyan]💰 Payments[/bold cyan]\n")
        
        table = Table()
        table.add_column("Amount", style="cyan")
        table.add_column("Status")
        table.add_column("Customer")
        table.add_column("Created")
        table.add_column("ID")
        
        for payment in payments.data:
            if status and payment.status != status:
                continue
            
            amount = payment.amount / 100
            currency = payment.currency.upper()
            
            status_color = {
                "succeeded": "green",
                "pending": "yellow", 
                "requires_action": "yellow",
                "failed": "red",
                "canceled": "red"
            }.get(payment.status, "white")
            
            from datetime import datetime
            created = datetime.fromtimestamp(payment.created).strftime("%Y-%m-%d")
            
            table.add_row(
                f"{currency} {amount:,.2f}",
                f"[{status_color}]{payment.status}[/{status_color}]",
                str(payment.customer or "-")[:20],
                created,
                payment.id[:20] + "..."
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@stripe_cli.command(name="subscriptions")
@click.option("--limit", default=20, type=int)
@click.option("--status", type=click.Choice(["active", "canceled", "past_due", "trialing"]))
def list_subscriptions(limit, status):
    """List subscriptions."""
    stripe = get_stripe_client()
    if not stripe:
        return
    
    try:
        params = {"limit": limit}
        if status:
            params["status"] = status
        
        subs = stripe.Subscription.list(**params)
        
        console.print("\n[bold cyan]📋 Subscriptions[/bold cyan]\n")
        
        table = Table()
        table.add_column("Customer", style="cyan")
        table.add_column("Status")
        table.add_column("Plan")
        table.add_column("Amount")
        table.add_column("ID")
        
        for sub in subs.data:
            status_color = {
                "active": "green",
                "trialing": "blue",
                "past_due": "yellow",
                "canceled": "red"
            }.get(sub.status, "white")
            
            plan = sub.items.data[0].price if sub.items.data else None
            amount = f"{plan.currency.upper()} {plan.unit_amount/100:,.2f}" if plan else "-"
            plan_name = plan.nickname or plan.id[:15] if plan else "-"
            
            table.add_row(
                str(sub.customer)[:20],
                f"[{status_color}]{sub.status}[/{status_color}]",
                plan_name,
                amount,
                sub.id[:20] + "..."
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@stripe_cli.command(name="invoices")
@click.option("--limit", default=20, type=int)
def list_invoices(limit):
    """List invoices."""
    stripe = get_stripe_client()
    if not stripe:
        return
    
    try:
        invoices = stripe.Invoice.list(limit=limit)
        
        console.print("\n[bold cyan]📄 Invoices[/bold cyan]\n")
        
        table = Table()
        table.add_column("Number", style="cyan")
        table.add_column("Status")
        table.add_column("Customer")
        table.add_column("Amount")
        table.add_column("Due Date")
        
        for inv in invoices.data:
            status_color = {
                "paid": "green",
                "open": "yellow",
                "draft": "muted",
                "void": "red",
                "uncollectible": "red"
            }.get(inv.status, "white")
            
            amount = f"{inv.currency.upper()} {inv.amount_due/100:,.2f}"
            
            from datetime import datetime
            due = datetime.fromtimestamp(inv.due_date).strftime("%Y-%m-%d") if inv.due_date else "-"
            
            table.add_row(
                inv.number or "-",
                f"[{status_color}]{inv.status}[/{status_color}]",
                str(inv.customer_email or inv.customer)[:25],
                amount,
                due
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@stripe_cli.command(name="products")
@click.option("--limit", default=20, type=int)
def list_products(limit):
    """List products."""
    stripe = get_stripe_client()
    if not stripe:
        return
    
    try:
        products = stripe.Product.list(limit=limit, active=True)
        
        console.print("\n[bold cyan]📦 Products[/bold cyan]\n")
        
        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("Active")
        table.add_column("ID")
        
        for product in products.data:
            active = "[green]✓[/green]" if product.active else "[red]✗[/red]"
            table.add_row(product.name, active, product.id)
        
        console.print(table)
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


@stripe_cli.command(name="refund")
@click.argument("payment_intent_id")
@click.option("--amount", type=int, help="Amount in cents (partial refund)")
@click.option("--reason", type=click.Choice(["duplicate", "fraudulent", "requested_by_customer"]))
def create_refund(payment_intent_id, amount, reason):
    """Create a refund."""
    stripe = get_stripe_client()
    if not stripe:
        return
    
    try:
        params = {"payment_intent": payment_intent_id}
        if amount:
            params["amount"] = amount
        if reason:
            params["reason"] = reason
        
        refund = stripe.Refund.create(**params)
        
        console.print(f"[success]✓ Refund created: {refund.id}[/success]")
        console.print(f"[muted]Amount: {refund.currency.upper()} {refund.amount/100:,.2f}[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = stripe_cli

if __name__ == "__main__":
    stripe_cli()
