import mysql.connector

def add_test_balance():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='dailywealth'
        )
        cursor = conn.cursor()

        user_id = 26
        test_amount = 100.0

        # Check if wallet exists
        cursor.execute("SELECT balance, withdrawable FROM wallets WHERE user_id = %s", (user_id,))
        wallet = cursor.fetchone()

        if wallet:
            # Update existing wallet
            cursor.execute("""
                UPDATE wallets 
                SET balance = balance + %s, 
                    withdrawable = withdrawable + %s,
                    total_earned = total_earned + %s
                WHERE user_id = %s
            """, (test_amount, test_amount, test_amount, user_id))
            print(f"✅ Added ${test_amount} to user {user_id}'s wallet")
        else:
            # Create wallet if doesn't exist
            cursor.execute("""
                INSERT INTO wallets (user_id, balance, withdrawable, total_earned)
                VALUES (%s, %s, %s, %s)
            """, (user_id, test_amount, test_amount, test_amount))
            print(f"✅ Created wallet with ${test_amount} for user {user_id}")

        # Show final balance
        cursor.execute("SELECT balance, withdrawable FROM wallets WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        print(f"\n📊 User {user_id} Balance:")
        print(f"   Total: ${result[0]}")
        print(f"   Withdrawable: ${result[1]}")

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_test_balance()
