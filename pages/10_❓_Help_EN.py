import streamlit as st
from utils.sidebar import render_sidebar

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="❓ Help & User Guide – Internal",
    page_icon="❓",
    layout="wide"
)
render_sidebar()

st.title("❓ HELP & USER GUIDE")
st.markdown("### Case Management Application – **Internal Cabinet Use**")

# =====================================================
# TABS
# =====================================================
tabs = st.tabs([
    "📘 1. Purpose",
    "🧭 2. General Navigation",
    "📁 3. Case Management",
    "💰 4. Billing & Escrow",
    "📊 5. Analytics & KPIs",
    "📤 6. Exports & PDFs",
    "⚠️ 7. Best Practices",
    "❓ 8. FAQ",
    "📄 9. Printing & PDF"
])

# =====================================================
# 1. PURPOSE
# =====================================================
with tabs[0]:
    st.subheader("1. Application Purpose")

    st.write("""
This application has been designed to centralize **all case management operations** of the firm, without requiring any technical knowledge.

It allows:

- Administrative case tracking (statuses, dates)
- Financial tracking (fees, payments, balances)
- Full **escrow management**
- Parent / sub-case organization
- Global analytics with KPIs
- Professional exports (Excel / PDF)

👉 **All calculations are automatic.**
No manual financial tracking is required.
    """)

# =====================================================
# 2. GENERAL NAVIGATION (VERY DETAILED)
# =====================================================
with tabs[1]:
    st.subheader("2. General Navigation")

    st.write("""
The **left sidebar menu** is the main navigation entry point of the application.

It allows access to all modules while keeping data consistent.
    """)

    st.markdown("""
### Main Pages

- **🏠 Dashboard – Global View**  
  Overall firm activity, KPIs, and filters.

- **📁 Case List**  
  Complete list of all cases with advanced filters.

- **➕ New Case**  
  Create a parent case or a sub-case.

- **✏️ Edit Case**  
  Central daily management page.

- **📊 Analytics**  
  Advanced statistics, multi-year comparisons, charts.

- **💰 Escrow**  
  Escrow tracking, actions, and history.

- **🛂 Visa**  
  Visa reference list.

- **💲 Fees**  
  Visa-based pricing with effective dates and history.

- **📤 Export Excel / JSON**  
  Full exports for audit or archival.

- **📄 Case File (PDF)**  
  Individual case summary with PDF export.

- **📁 Group Case File (PDF)**  
  Parent + sub-cases grouped PDF.

- **⚙️ Settings**  
  Technical tools (Excel import, JSON validation, Dropbox diagnostics).

- **❓ Help**  
  This documentation.
    """)

    st.info("""
Tip:
If a page does not appear in the menu:
1️⃣ Check the exact filename in `/pages`
2️⃣ Ensure it is referenced in the sidebar
    """)

# =====================================================
# 3. CASE MANAGEMENT
# =====================================================
with tabs[2]:
    st.subheader("3. Case Management (Parent & Sub-Cases)")

    st.write("""
### 3.1 Case Types

The application manages **two types of cases**:
    """)

    st.markdown("""
#### 📁 Parent Case
- Simple number (e.g., `13068`)
- Main client file
- Contains general information

#### 📎 Sub-Case
- Numbering: `13068-1`, `13068-2`, etc.
- Attached to a parent case
- May have:
  - A **different visa**
  - **Different fees**
  - **Separate payments**
    """)

    st.write("""
👉 Sub-cases are used when:
- A client has multiple procedures
- Different visas are required
- Separate financial tracking is needed
    """)

    st.markdown("---")

    st.write("""
### 3.2 Creating a Case

In **➕ New Case**:

1. Choose the type:
   - Parent case
   - Sub-case (select parent)

2. Fill in:
   - Client name
   - Creation date
   - Category / Sub-category
   - Visa

3. Billing:
   - Legal fees
   - Additional fees

4. Initial payment:
   - **Payment 1**
   - Payment date
   - Payment method (Check / Credit Card / Wire / Venmo)
    """)

    st.warning("""
Important:
Payments 2, 3, and 4 are entered later in **Edit Case**.
    """)

    st.markdown("---")

    st.write("""
### 3.3 Editing a Case

In **✏️ Edit Case**, you can:

- Update administrative information
- Manage all payments
- Track balances
- Manage escrow
- Update statuses
- Add internal comments (always saved)
    """)

# =====================================================
# 4. BILLING & ESCROW
# =====================================================
with tabs[3]:
    st.subheader("4. Billing & Escrow")

    st.write("""
### Billing
- Legal fees (USD)
- Additional fees
- Total billed (automatic)
- Total collected
- Outstanding balance

### Escrow Rules (CRITICAL)

- As long as the case is **not accepted, refused, or canceled**:
  👉 **ALL payments remain in escrow**
- When the case becomes:
  - Accepted
  - Refused
  - Canceled  
  👉 Escrow moves to **Escrow to Claim**
- Final step:
  👉 **Escrow Claimed**

Full escrow history is preserved.
    """)

# =====================================================
# 5. ANALYTICS & KPIs
# =====================================================
with tabs[4]:
    st.subheader("5. Analytics & KPIs")

    st.write("""
Available KPIs:
- Total number of cases
- Sent cases
- Accepted / Refused / Canceled cases
- Paid / unpaid cases
- Negative balances
- Total escrow amount

Filters:
- Year / multi-year
- Period comparison
- Category / Sub-category / Visa
- Case statuses
    """)

# =====================================================
# 6. EXPORTS
# =====================================================
with tabs[5]:
    st.subheader("6. Exports")

    st.write("""
### Excel Export
- Multi-sheet
- Timestamped
- No digital signature
- Audit-ready

### PDF Export
- Individual case file
- Group (parent + sub-cases)
- Internal help manual
    """)

# =====================================================
# 7. BEST PRACTICES
# =====================================================
with tabs[6]:
    st.subheader("7. Best Practices")

    st.markdown("""
✔ Always use filters  
✔ Never manually edit the JSON  
✔ Verify payment dates  
✔ Use sub-cases for multiple visas  
✔ Archive regularly using exports
    """)

# =====================================================
# 8. FAQ
# =====================================================
with tabs[7]:
    st.subheader("8. FAQ")

    st.markdown("""
**Why does a case not appear in a KPI?**  
➡ Check active filters.

**Why is escrow higher than expected?**  
➡ All payments remain in escrow until the case is finalized.

**Can I change a visa on a sub-case?**  
➡ Yes, independently from the parent.
    """)

# =====================================================
# 9. PRINTING & PDF
# =====================================================
with tabs[8]:
    st.subheader("9. Printing & PDF")

    st.write("""
This help guide is:
- Fully viewable in the application
- Printable
- Exportable to PDF
- Available in French and English
    """)

    st.button("📄 Generate PDF Manual (to be enabled)")