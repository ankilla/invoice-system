


Here is the complete, beginner-friendly, A-Z documentation in Markdown format. You can save this text as a `.md` file (for example, `Documentation.md`) and open it in any Markdown viewer, code editor (like VS Code), or even directly on GitHub.

***

# Invoice Gen Pro - Developer & Customization Documentation

Welcome to the beginner-friendly guide to customizing your Invoice Application! This guide will teach you exactly where and how to make changes to your PDF invoices, web pages, and database without breaking the app.

---

## 🛑 Important: Before You Begin (How this App Works)

When you first run `main.py`, it acts as a **generator**. It creates a folder called `templates/`, a folder called `static/`, and a file called `app.py`. 

*   **For permanent, ongoing edits:** You should edit **`app.py`** and the HTML files inside the **`templates/`** folder. 
*   **Do not** keep running `main.py` over and over again if you are editing `app.py` directly, because running `main.py` will overwrite all your hard work!

Whenever you make changes to `app.py`, you must **restart the Python server** to see the changes. If you edit an HTML file in the `templates/` folder, you just need to **refresh your web browser**.

---

## Part 1: Customizing the PDF Invoice (The Core)

All the magic for the PDF happens inside `app.py` in a single function named:
`def generate_pdf_file(inv, items, owner, pdf_path):`

### Understanding the Canvas (Very Important!)
The PDF is drawn using X and Y coordinates:
*   **X (Horizontal):** Starts at `0` on the **left** edge and increases as you move **right**.
*   **Y (Vertical):** Starts at `0` on the **bottom** edge and increases as you move **up** to the top of the page.

### 1. How to Change Logo Size and Position
Search for this line inside the `generate_pdf_file` function:
```python
c.drawImage(os.path.join(app.config['OWNER_FOLDER'], owner['logo_path']), x_start + 2, y_top - 78, width=80, height=76, preserveAspectRatio=True, mask='auto')
```
*   **To make the logo larger:** Change `width=80` and `height=76` to bigger numbers (e.g., `width=120, height=114`).
*   **To move it right:** Increase the number after `x_start + ` (e.g., `x_start + 20`).
*   **To move it up/down:** Change the `y_top - 78`. (Subtracting a *smaller* number moves it *up*, subtracting a *bigger* number moves it *down*).

### 2. How to Change QR Code Size and Position
Search for this line:
```python
c.drawImage(os.path.join(app.config['OWNER_FOLDER'], owner['qr_path']), x_start + 65, 152, width=70, height=70, preserveAspectRatio=True, mask='auto')
```
*   **To change size:** Adjust `width=70` and `height=70`.
*   **To move it:** Adjust `x_start + 65` (Left/Right) and `152` (Up/Down).

### 3. How to Adjust Invoice Column Widths
The table columns are controlled by variables named `c0` through `c8`. They are calculated from right to left (`c8` is the far right edge, `c0` is the far left edge).
Search for this block:
```python
c8 = x_end
c7 = c8 - max_n_w
c6 = c7 - 35
c5 = c6 - max_g_w
c4 = c5 - max_r_w
c3 = c4 - 40
c2 = 110
c1 = 60
c0 = x_start
```
*   **To make the S.No column wider:** Increase `c1` (e.g., change `60` to `70`).
*   **To make the Code column wider:** Increase `c2` (e.g., change `110` to `140`).
*   **To make Qty wider:** Increase `40` in `c3 = c4 - 40` to `c4 - 50`.
*   *Note:* Because columns push against each other, changing one might require tweaking the text positions (explained below).

### 4. How to Fix Text Alignment inside Columns
If you move a column line, you need to move the text inside it so it doesn't overlap the lines.
Search for the `c.drawString` lines for the **Table Header**:
```python
c.drawString(cols[0]+5, y_table_top-15, "Sn")
c.drawString(cols[1]+5, y_table_top-15, "Code")
```
And the **Table Rows**:
```python
c.drawString(cols[0]+8, y_item, str(idx+1))
c.drawString(cols[1]+2, y_item, str(item.get('product_code', '')))
```
*   Change the `+5`, `+8`, or `+2` to add more padding inside the column.

### 5. How to Adjust the Space Between Items (Row Height)
If your product descriptions are crashing into each other, you need more vertical space between rows.
Search for this exact line at the end of the item loop:
```python
y_item -= 15
```
*   **To add more space:** Change `15` to `20` or `25`.
*   *Note:* You must also change this in the dummy loop above it that calculates page breaks! Find `sim_y -= 15` and change it to match your new number.

### 6. Adjusting Header, Footer, and Table Heights
The PDF is divided into horizontal sections using "Y" coordinate variables.
Look for this block:
```python
y_copies_bot = y_top - 80     # Bottom line of the top company info box
y_det_top = y_copies_bot      # Top of the Invoice Details box
y_det_bot = y_det_top - 75    # Bottom of the Invoice Details box
y_addr_bot = y_det_bot - 110  # Bottom of the Billing Address box
y_table_top = y_addr_bot      # Top line of the Items Table
y_table_head_bot = y_table_top - 30 # Bottom line of the Table Header
```
*   **Want more space for Company Name/Address?** Change `y_copies_bot = y_top - 80` to `y_top - 100`. (You will also need to adjust the Y coordinates of where the text is drawn so it sits nicely in the new bigger box).
*   **Want more space for Customer Address?** Change `- 110` in `y_addr_bot` to `- 130`.

### 7. How to Change Font Sizes
Whenever you see `bFont(12)` or `rFont(9)`, that sets the text size!
*   `bFont(12)` = Bold Font, Size 12.
*   `rFont(9)` = Regular Font, Size 9.
Just change the number inside the brackets right before a `c.drawString(...)` command.

---

## Part 2: Customizing the Web Pages (HTML/UI)

All the visual parts of the application (colors, buttons, forms) live in the `templates/` folder.

### 1. Changing Colors and Styles
The application uses **Bootstrap 5**. You don't need to write CSS; you just change the "class" names in the HTML.
*   **Colors:** `primary` (Blue), `success` (Green), `danger` (Red), `warning` (Yellow), `dark` (Black), `info` (Light Blue).
*   **Text color:** `text-primary`, `text-success`, etc.
*   **Backgrounds:** `bg-primary`, `bg-light`, `bg-dark`, etc.
*   **Buttons:** `btn-primary`, `btn-danger`.
*   *Example:* Open `templates/invoice_form.html`. Find `<button type="submit" class="btn btn-success...`. Change `btn-success` to `btn-primary` and your save button turns blue!

### 2. How to Add a New Field to the Invoice Form
If you want to add a new text box (e.g., "Vehicle Number"):
1.  **HTML:** Open `templates/invoice_form.html`. Find the transportation section and paste this:
    ```html
    <div class="col-md-3">
        <label>Vehicle No.</label>
        <input type="text" name="vehicle_no" class="form-control" value="{{inv.vehicle_no if inv else ''}}">
    </div>
    ```
2.  **Database:** Open `app.py`. Find `init_db()` and add this line inside it:
    ```python
    alter_table(conn, 'invoices', 'vehicle_no', 'TEXT')
    ```
3.  **Python Backend:** In `app.py`, find `handle_invoice()`. Look at the `INSERT INTO` and `UPDATE` SQL commands. You have to add `vehicle_no` to the list of columns being saved, and add `request.form.get('vehicle_no', '')` to the list of data being pulled from the form.
4.  **PDF (Optional):** Go to `generate_pdf_file` and draw it on the PDF using `c.drawString(...)`.

---

## Part 3: Fixing Common Errors & Troubleshooting

### 1. "Rupees in Words" is overlapping the Net Amount box!
This happens if the final bill amount is massive (e.g., Crores) and the text becomes super long. 
*   **The Fix:** Find `char_limit = 60` in the `generate_pdf_file` function (under the Net Amount section). Change it to `50` or `45` to force the text to wrap into a new line sooner.

### 2. Internal Server Error (500)
This means there is a typo in `app.py`.
*   **The Fix:** Look at the Terminal/Command Prompt where your Python server is running. Scroll to the bottom. It will tell you the exact **Line Number** and the error (e.g., `SyntaxError` or `KeyError`).

### 3. I updated HTML but the browser isn't showing it!
Browsers cache (save) old HTML files to load pages faster.
*   **The Fix:** Do a "Hard Refresh". Press `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac).

### 4. How do I backup my database manually?
Your entire application's data is stored in one single file: `db/invoice_system.db`.
*   **To Backup:** Simply copy/paste that file somewhere safe (like a USB drive or Google Drive).
*   *Alternatively,* you can use the built-in "System -> Export Database" button in the app.

---

## Part 4: A Quick Map of Files & Functions

*   `app.py` 👉 The Brains. Connects the database, handles logins, saves data, generates PDFs.
    *   `init_db()` 👉 Creates tables and adds new columns.
    *   `dashboard()` 👉 Controls the home page math (revenue, pending).
    *   `handle_invoice()` 👉 Saves/Edits the invoice in the database.
    *   `generate_pdf_file()` 👉 Draws the PDF invoice.
*   `templates/base.html` 👉 The skeleton of the app. Has the top Navigation bar. Edit this to change the menu links.
*   `templates/invoice_form.html` 👉 The screen where you type in items, quantities, and rates. Contains the JavaScript for Auto-Calculations (`doTotals()`).
*   `static/help.json` 👉 The file that stores the Help & FAQ questions. Edit this in Notepad to add your own guides!
