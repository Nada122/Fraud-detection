from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For flash messages
db_path = r"C:\Users\Eng_E\OneDrive\MSC\Semester 2\Software Engineering Studio\Project\Code\DB API\Bank.sqlite"



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = get_db()  # Use the get_db function
    cursor = conn.cursor()
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of records per page

    try:
        # Get paginated fraud data
        cursor.execute("SELECT * FROM Input LIMIT ? OFFSET ?", (per_page, (page - 1) * per_page))
        columns = [description[0] for description in cursor.description]
        fraud_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Get total number of records for pagination
        cursor.execute("SELECT COUNT(*) FROM Input")
        total_records = cursor.fetchone()[0]

        # Get statistics
        cursor.execute("SELECT COUNT(DISTINCT AccountID) FROM Input")
        unique_accounts = cursor.fetchone()[0]
        cursor.execute("SELECT AVG(TransactionAmount) FROM Input")
        avg_transaction = cursor.fetchone()[0]
        
        # Calculate total pages
        total_pages = (total_records + per_page - 1) // per_page

        return render_template(
            'dashboard.html',
            fraud_data=fraud_data,
            total_records=total_records,
            unique_accounts=unique_accounts,
            avg_transaction=round(avg_transaction, 2) if avg_transaction else 0,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    except sqlite3.Error as e:
        flash(f"Database error: {str(e)}", "error")
        return render_template('dashboard.html', fraud_data=[], page=page, per_page=per_page, total_pages=0)
    finally:
        if conn:
            conn.close()

@app.route('/view/<int:index>')
def view_record(index):
    conn = get_db() # Use the get_db function
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM Input WHERE \"Index\"=?", (index,))
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        
        if row:
            record = dict(zip(columns, row))
            return render_template('view_record.html', record=record)
        else:
            flash("Record not found", "error")
            return redirect(url_for('dashboard'))
    except sqlite3.Error as e:
        flash(f"Database error: {str(e)}", "error")
        return redirect(url_for('dashboard'))
    finally:
        if conn:
            conn.close()

@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if request.method == 'GET':
        return render_template('add_record.html')
    
    elif request.method == 'POST':
        conn = get_db() # Use the get_db function
        cursor = conn.cursor()
        
        try:
            # Extract data from form
            transaction_id = request.form.get('TransactionID')
            account_id = request.form.get('AccountID')
            transaction_amount = request.form.get('TransactionAmount')
            transaction_date = request.form.get('TransactionDate')
            transaction_type = request.form.get('TransactionType')
            location = request.form.get('Location')
            device_id = request.form.get('DeviceID')
            ip_address = request.form.get('IP_Address')
            merchant_id = request.form.get('MerchantID')
            channel = request.form.get('Channel')
            customer_age = request.form.get('CustomerAge')
            customer_occupation = request.form.get('CustomerOccupation')
            transaction_duration = request.form.get('TransactionDuration')
            login_attempts = request.form.get('LoginAttempts')
            account_balance = request.form.get('AccountBalance')
            previous_transaction_date = request.form.get('PreviousTransactionDate')
            account_profile_id = request.form.get('AccountProfileID')

            if all([transaction_id, account_id, transaction_amount, transaction_date]):
                cursor.execute("""
                    INSERT INTO Input (TransactionID, AccountID, TransactionAmount, TransactionDate, TransactionType, 
                                        Location, DeviceID, "IP Address", MerchantID, Channel, CustomerAge, 
                                        CustomerOccupation, TransactionDuration, LoginAttempts, AccountBalance, 
                                        PreviousTransactionDate, AccountProfileID)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (transaction_id, account_id, transaction_amount, transaction_date, transaction_type, 
                      location, device_id, ip_address, merchant_id, channel, customer_age, 
                      customer_occupation, transaction_duration, login_attempts, account_balance, 
                      previous_transaction_date, account_profile_id))
                
                conn.commit()
                flash("Record added successfully", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("TransactionID, AccountID, TransactionAmount, and TransactionDate are required fields", "error")
                return render_template('add_record.html')
                
        except sqlite3.Error as e:
            conn.rollback()
            flash(f"Database error: {str(e)}", "error")
            return render_template('add_record.html')
        finally:
            if conn:
                conn.close()

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_record(index):
    conn = get_db() # Use the get_db function
    cursor = conn.cursor()
    
    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM Input WHERE \"Index\"=?", (index,))
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            
            if row:
                record = dict(zip(columns, row))
                return render_template('edit_record.html', record=record)
            else:
                flash("Record not found", "error")
                return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            flash(f"Database error: {str(e)}", "error")
            return redirect(url_for('dashboard'))
        finally:
            if conn:
                conn.close()
    
    elif request.method == 'POST':
        try:
            # Extract form data
            data = {
                'TransactionID': request.form.get('TransactionID'),
                'AccountID': request.form.get('AccountID'),
                'TransactionAmount': request.form.get('TransactionAmount'),
                'TransactionDate': request.form.get('TransactionDate'),
                'TransactionType': request.form.get('TransactionType'),
                'Location': request.form.get('Location'),
                'DeviceID': request.form.get('DeviceID'),
                'IP Address': request.form.get('IP_Address'),
                'MerchantID': request.form.get('MerchantID'),
                'Channel': request.form.get('Channel'),
                'CustomerAge': request.form.get('CustomerAge'),
                'CustomerOccupation': request.form.get('CustomerOccupation'),
                'TransactionDuration': request.form.get('TransactionDuration'),
                'LoginAttempts': request.form.get('LoginAttempts'),
                'AccountBalance': request.form.get('AccountBalance'),
                'PreviousTransactionDate': request.form.get('PreviousTransactionDate'),
                'AccountProfileID': request.form.get('AccountProfileID')
            }
            
            sql_parts = []
            params = []
            
            for key, value in data.items():
                if value is not None and value != '':
                    if key == 'IP Address':
                        sql_parts.append("\"IP Address\"=?")
                    else:
                        sql_parts.append(f"{key}=?")
                    params.append(value)
            
            if sql_parts:
                sql = f"UPDATE Input SET {', '.join(sql_parts)} WHERE \"Index\"=?"
                params.append(index)
                cursor.execute(sql, params)
                conn.commit()
                flash("Record updated successfully", "success")
            else:
                flash("No changes were made", "info")
            
            return redirect(url_for('dashboard'))
        except sqlite3.Error as e:
            conn.rollback()
            flash(f"Database error: {str(e)}", "error")
            return redirect(url_for('edit_record', index=index))
        finally:
            if conn:
                conn.close()

@app.route('/delete/<int:index>', methods=['POST'])
def delete_record(index):
    conn = get_db() # Use the get_db function
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Input WHERE \"Index\"=?", (index,))
        conn.commit()
        flash("Record deleted successfully", "success")
    except sqlite3.Error as e:
        conn.rollback()
        flash(f"Database error: {str(e)}", "error")
    finally:
        if conn:
            conn.close()
            
    return redirect(url_for('dashboard'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html')
    
    elif request.method == 'POST':
        search_term = request.form.get('search_term')
        search_field = request.form.get('search_field')
        
        if not search_term or not search_field:
            flash("Please provide both search term and field", "error")
            return render_template('search.html')
        
        conn = get_db() # Use the get_db function
        cursor = conn.cursor()
        
        try:
            # Handle special case for IP Address which has a space
            if search_field == "IP_Address":
                sql_field = "\"IP Address\""
            else:
                sql_field = search_field
                
            query = f"SELECT * FROM Input WHERE {sql_field} LIKE ?"
            cursor.execute(query, (f"%{search_term}%",))
            
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return render_template('search_results.html', results=results, search_term=search_term, search_field=search_field)
            
        except sqlite3.Error as e:
            flash(f"Database error: {str(e)}", "error")
            return render_template('search.html')
        finally:
            if conn:
                conn.close()

# API Endpoints (keeping the original API functionality)
@app.route('/api/fraud_data', methods=['GET', 'POST'])
def fraud_data_list():
    conn = get_db() # Use the get_db function
    cursor = conn.cursor()

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM Input")
            columns = [description[0] for description in cursor.description]
            fraud_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return jsonify(fraud_data), 200
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if conn:
                conn.close()

    elif request.method == 'POST':
        try:
            data = request.get_json()
            transaction_id = data.get('TransactionID')
            account_id = data.get('AccountID')
            transaction_amount = data.get('TransactionAmount')
            transaction_date = data.get('TransactionDate')
            transaction_type = data.get('TransactionType')
            location = data.get('Location')
            device_id = data.get('DeviceID')
            ip_address = data.get('IP Address')
            merchant_id = data.get('MerchantID')
            channel = data.get('Channel')
            customer_age = data.get('CustomerAge')
            customer_occupation = data.get('CustomerOccupation')
            transaction_duration = data.get('TransactionDuration')
            login_attempts = data.get('LoginAttempts')
            account_balance = data.get('AccountBalance')
            previous_transaction_date = data.get('PreviousTransactionDate')
            account_profile_id = data.get('AccountProfileID')

            if all([transaction_id, account_id, transaction_amount, transaction_date]):
                cursor.execute("""
                    INSERT INTO Input (TransactionID, AccountID, TransactionAmount, TransactionDate, TransactionType, Location, DeviceID, "IP Address", MerchantID, Channel, CustomerAge, CustomerOccupation, TransactionDuration, LoginAttempts, AccountBalance, PreviousTransactionDate, AccountProfileID)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (transaction_id, account_id, transaction_amount, transaction_date, transaction_type, location, device_id, ip_address, merchant_id, channel, customer_age, customer_occupation, transaction_duration, login_attempts, account_balance, previous_transaction_date, account_profile_id))
                conn.commit()
                return jsonify({"message": "data added successfully"}), 201
            else:
                return jsonify({"error": "TransactionID, AccountID, TransactionAmount, and TransactionDate are required fields"}), 400
        except sqlite3.Error as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            if conn:
                conn.close()

@app.route('/api/fraud_data/<int:index>', methods=['GET', 'PUT', 'DELETE'])
def fraud_data_item(index):
    conn = get_db() # Use the get_db function
    cursor = conn.cursor()

    if request.method == 'GET':
        try:
            cursor.execute("SELECT * FROM Input WHERE \"Index\"=?", (index,))
            columns = [description[0] for description in cursor.description]
            row = cursor.fetchone()
            fraud_data = dict(zip(columns, row)) if row else None
            if fraud_data:
                return jsonify(fraud_data), 200
            else:
                return jsonify({"error": "data not found"}), 404
        except sqlite3.Error as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if conn:
                conn.close()

    elif request.method == 'PUT':
        try:
            data = request.get_json()
            # Create a list of fields to update
            sql_parts = []
            params = []
            
            for key, value in data.items():
                if value is not None:
                    if key == 'IP Address':
                        sql_parts.append("\"IP Address\"=?")
                    else:
                        sql_parts.append(f"{key}=?")
                    params.append(value)
            
            if sql_parts:
                sql = f"UPDATE Input SET {', '.join(sql_parts)} WHERE \"Index\"=?"
                params.append(index)
                cursor.execute(sql, params)
                conn.commit()
                return jsonify({"message": "data updated successfully"}), 200
            else:
                return jsonify({"error": "No fields provided for update"}), 400
        except sqlite3.Error as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            if conn:
                conn.close()

    elif request.method == 'DELETE':
        try:
            cursor.execute("DELETE FROM Input WHERE \"Index\"=?", (index,))
            conn.commit()
            return jsonify({"message": "data deleted successfully"}), 200
        except sqlite3.Error as e:
            conn.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            if conn:
                conn.close()

@app.route('/api/fraud_data/account/<account_id>', methods=['GET'])
def get_fraud_by_account(account_id):
    conn = get_db() # Use the get_db function
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Input WHERE AccountID=?", (account_id,))
        columns = [description[0] for description in cursor.description]
        fraud_data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        if fraud_data:
            return jsonify(fraud_data), 200
        else:
            return jsonify({"message": f"no data found for AccountID: {account_id}"}), 404
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=False)
