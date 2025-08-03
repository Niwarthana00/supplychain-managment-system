import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter

def generate_plots(chain):
    if len(chain) <= 1:
        return {'plots': None, 'stats': None}

    transactions = []
    for block in chain:
        transactions.extend(block['transactions'])

    if not transactions:
        return {'plots': None, 'stats': None}

    df = pd.DataFrame(transactions)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    plots = {}
    stats = {}

    # --- STATS ---
    stats['total_products'] = len(df)
    stats['unique_products'] = df['product_name'].nunique()
    stats['most_common_product'] = df['product_name'].mode()[0] if not df['product_name'].empty else 'N/A'
    stats['latest_transaction'] = df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S') if not df['timestamp'].empty else 'N/A'

    # --- PLOTS ---
    plt.style.use('seaborn-v0_8-darkgrid')

    # Plot 1: Product Distribution by Name (Pie Chart)
    plt.figure(figsize=(8, 8))
    product_counts = df['product_name'].value_counts()
    plt.pie(product_counts, labels=product_counts.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title('Product Distribution by Name', fontsize=16, fontweight='bold')
    plt.ylabel('')
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plots['product_distribution'] = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Plot 2: Number of Transactions per Product (Bar Chart)
    plt.figure(figsize=(10, 6))
    transactions_per_product = df['product_name'].value_counts()
    transactions_per_product.plot(kind='bar', color='skyblue')
    plt.title('Number of Transactions per Product', fontsize=16, fontweight='bold')
    plt.xlabel('Product Name', fontsize=12)
    plt.ylabel('Number of Transactions', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plots['transactions_per_product'] = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Plot 3: Transactions Over Time (Line Chart)
    plt.figure(figsize=(12, 6))
    transactions_over_time = df.set_index('timestamp').resample('D').size()
    transactions_over_time.plot(kind='line', marker='o', linestyle='-', color='green')
    plt.title('Transactions Over Time', fontsize=16, fontweight='bold')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Transactions', fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plots['transactions_over_time'] = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Plot 4: Products by Location (Bar Chart)
    plt.figure(figsize=(10, 6))
    location_counts = df['location'].value_counts()
    location_counts.plot(kind='bar', color='coral')
    plt.title('Products by Location', fontsize=16, fontweight='bold')
    plt.xlabel('Location', fontsize=12)
    plt.ylabel('Number of Products', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plots['products_by_location'] = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return {'plots': plots, 'stats': stats}
