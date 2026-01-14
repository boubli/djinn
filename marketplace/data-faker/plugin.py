"""
Data Faker Plugin for DJINN
Generate fake data for testing.
"""
import click
from rich.console import Console
from rich.table import Table
import json
import random
import string
from datetime import datetime, timedelta

console = Console()

PLUGIN_NAME = "data-faker"
PLUGIN_VERSION = "1.0.0"
PLUGIN_AUTHOR = "DJINN Team"
PLUGIN_DESCRIPTION = "Generate fake data for testing and development."


# Data pools
FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
               "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Margaret"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
              "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White"]

DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "proton.me", "icloud.com"]

STREETS = ["Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St", "Washington Blvd",
           "Park Ave", "Lake Dr", "River Rd", "Hill St", "Forest Ave", "Ocean Dr", "Mountain Rd"]

CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio",
          "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus"]

COMPANIES = ["Acme Corp", "Globex", "Initech", "Umbrella Corp", "Stark Industries", "Wayne Enterprises",
             "Oscorp", "Cyberdyne", "Weyland-Yutani", "Tyrell Corp", "Soylent Corp", "Aperture Science"]

PRODUCTS = ["Widget Pro", "Super Gadget", "Premium Service", "Basic Plan", "Enterprise Solution",
            "Starter Kit", "Professional Package", "Ultimate Bundle", "Essential Tools", "Advanced Suite"]


def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_email(name=None):
    if not name:
        name = random_name()
    parts = name.lower().split()
    styles = [
        f"{parts[0]}.{parts[1]}",
        f"{parts[0][0]}{parts[1]}",
        f"{parts[0]}{random.randint(1, 999)}",
        f"{parts[0]}_{parts[1]}"
    ]
    return f"{random.choice(styles)}@{random.choice(DOMAINS)}"


def random_phone():
    return f"+1 ({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"


def random_address():
    return f"{random.randint(1, 9999)} {random.choice(STREETS)}, {random.choice(CITIES)}"


def random_date(start_year=2020, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = (end - start).days
    random_days = random.randint(0, delta)
    return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")


def random_uuid():
    import uuid
    return str(uuid.uuid4())


def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@click.group()
def fake():
    """Fake data generation commands."""
    pass


@fake.command(name="user")
@click.option("--count", "-n", default=1, type=int, help="Number of users")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def generate_user(count, as_json):
    """Generate fake user data."""
    users = []
    
    for _ in range(count):
        name = random_name()
        user = {
            "id": random_uuid(),
            "name": name,
            "email": random_email(name),
            "phone": random_phone(),
            "address": random_address(),
            "created_at": random_date()
        }
        users.append(user)
    
    if as_json:
        output = users if count > 1 else users[0]
        console.print_json(data=output)
    else:
        table = Table(title=f"Generated Users ({count})")
        table.add_column("ID", style="cyan")
        table.add_column("Name")
        table.add_column("Email")
        table.add_column("Phone")
        
        for user in users[:20]:
            table.add_row(user["id"][:8] + "...", user["name"], user["email"], user["phone"])
        
        console.print(table)


@fake.command(name="company")
@click.option("--count", "-n", default=1, type=int)
@click.option("--json", "as_json", is_flag=True)
def generate_company(count, as_json):
    """Generate fake company data."""
    companies = []
    
    for _ in range(count):
        company = {
            "id": random_uuid(),
            "name": random.choice(COMPANIES) + " " + random.choice(["Inc", "LLC", "Corp", "Ltd"]),
            "industry": random.choice(["Technology", "Finance", "Healthcare", "Retail", "Manufacturing"]),
            "employees": random.randint(10, 10000),
            "founded": random.randint(1950, 2020),
            "website": f"https://{random_string(8).lower()}.com"
        }
        companies.append(company)
    
    if as_json:
        output = companies if count > 1 else companies[0]
        console.print_json(data=output)
    else:
        for company in companies:
            console.print(f"[bold]{company['name']}[/bold]")
            console.print(f"  Industry: {company['industry']}")
            console.print(f"  Employees: {company['employees']}")
            console.print(f"  Website: {company['website']}")
            console.print()


@fake.command(name="product")
@click.option("--count", "-n", default=1, type=int)
@click.option("--json", "as_json", is_flag=True)
def generate_product(count, as_json):
    """Generate fake product data."""
    products = []
    
    for _ in range(count):
        product = {
            "id": random_uuid(),
            "name": random.choice(PRODUCTS),
            "sku": random_string(8).upper(),
            "price": round(random.uniform(9.99, 999.99), 2),
            "stock": random.randint(0, 1000),
            "category": random.choice(["Electronics", "Clothing", "Home", "Sports", "Books"]),
            "rating": round(random.uniform(1, 5), 1)
        }
        products.append(product)
    
    if as_json:
        output = products if count > 1 else products[0]
        console.print_json(data=output)
    else:
        table = Table(title=f"Generated Products ({count})")
        table.add_column("SKU", style="cyan")
        table.add_column("Name")
        table.add_column("Price")
        table.add_column("Stock")
        table.add_column("Rating")
        
        for product in products[:20]:
            table.add_row(
                product["sku"],
                product["name"],
                f"${product['price']}",
                str(product["stock"]),
                f"⭐ {product['rating']}"
            )
        
        console.print(table)


@fake.command(name="order")
@click.option("--count", "-n", default=1, type=int)
@click.option("--json", "as_json", is_flag=True)
def generate_order(count, as_json):
    """Generate fake order data."""
    orders = []
    
    for _ in range(count):
        items_count = random.randint(1, 5)
        items = []
        total = 0
        
        for _ in range(items_count):
            price = round(random.uniform(9.99, 199.99), 2)
            qty = random.randint(1, 3)
            items.append({
                "product": random.choice(PRODUCTS),
                "quantity": qty,
                "price": price
            })
            total += price * qty
        
        order = {
            "id": random_uuid(),
            "customer": random_name(),
            "email": random_email(),
            "items": items,
            "total": round(total, 2),
            "status": random.choice(["pending", "processing", "shipped", "delivered"]),
            "created_at": random_date()
        }
        orders.append(order)
    
    if as_json:
        output = orders if count > 1 else orders[0]
        console.print_json(data=output)
    else:
        for order in orders[:10]:
            status_color = {"pending": "yellow", "processing": "blue", "shipped": "cyan", "delivered": "green"}
            console.print(f"[bold]Order {order['id'][:8]}...[/bold]")
            console.print(f"  Customer: {order['customer']}")
            console.print(f"  Items: {len(order['items'])}")
            console.print(f"  Total: ${order['total']}")
            console.print(f"  Status: [{status_color.get(order['status'], 'white')}]{order['status']}[/]")
            console.print()


@fake.command(name="uuid")
@click.option("--count", "-n", default=1, type=int)
def generate_uuids(count):
    """Generate UUIDs."""
    for _ in range(count):
        console.print(random_uuid())


@fake.command(name="email")
@click.option("--count", "-n", default=1, type=int)
def generate_emails(count):
    """Generate random emails."""
    for _ in range(count):
        console.print(random_email())


@fake.command(name="phone")
@click.option("--count", "-n", default=1, type=int)
def generate_phones(count):
    """Generate random phone numbers."""
    for _ in range(count):
        console.print(random_phone())


@fake.command(name="address")
@click.option("--count", "-n", default=1, type=int)
def generate_addresses(count):
    """Generate random addresses."""
    for _ in range(count):
        console.print(random_address())


@fake.command(name="dataset")
@click.argument("schema_file")
@click.option("--count", "-n", default=10, type=int)
@click.option("--output", "-o", help="Output file")
def generate_dataset(schema_file, count, output):
    """Generate dataset from JSON schema."""
    try:
        with open(schema_file) as f:
            schema = json.load(f)
        
        data = []
        
        for _ in range(count):
            record = {}
            
            for field, field_type in schema.items():
                if field_type == "uuid":
                    record[field] = random_uuid()
                elif field_type == "name":
                    record[field] = random_name()
                elif field_type == "email":
                    record[field] = random_email()
                elif field_type == "phone":
                    record[field] = random_phone()
                elif field_type == "address":
                    record[field] = random_address()
                elif field_type == "date":
                    record[field] = random_date()
                elif field_type == "int":
                    record[field] = random.randint(1, 1000)
                elif field_type == "float":
                    record[field] = round(random.uniform(0, 1000), 2)
                elif field_type == "bool":
                    record[field] = random.choice([True, False])
                elif field_type == "string":
                    record[field] = random_string()
                else:
                    record[field] = field_type  # Use as literal value
            
            data.append(record)
        
        if output:
            with open(output, 'w') as f:
                json.dump(data, f, indent=2)
            console.print(f"[success]✓ Generated {count} records to {output}[/success]")
        else:
            console.print_json(data=data[:5])
            if count > 5:
                console.print(f"\n[muted]... and {count - 5} more[/muted]")
    except Exception as e:
        console.print(f"[error]Error: {e}[/error]")


main = fake

if __name__ == "__main__":
    fake()
