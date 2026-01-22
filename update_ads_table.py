import mysql.connector

def update_ads_watches():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='dailywealth'
        )
        cursor = conn.cursor()

        print("Updating 'ads_watches' table...")
        
        # Add ads_watched column
        try:
            cursor.execute("ALTER TABLE ads_watches ADD COLUMN ads_watched INT DEFAULT 0")
            print("Added 'ads_watched' to 'ads_watches'")
        except mysql.connector.Error as err:
            print(f"Error adding 'ads_watched': {err}")

        # Drop old watched column if exists
        try:
            cursor.execute("ALTER TABLE ads_watches DROP COLUMN watched")
            print("Dropped 'watched' from 'ads_watches'")
        except mysql.connector.Error as err:
            print(f"Info: {err}")

        conn.commit()
        print("\nAdsWatch table update completed successfully!")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Critical error: {e}")

if __name__ == "__main__":
    update_ads_watches()
