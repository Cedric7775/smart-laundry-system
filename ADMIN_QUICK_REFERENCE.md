# 🎯 Admin Dashboard Quick Reference Guide

## Getting Started

### Access Admin Panel

1. Go to `admin.html`
2. System checks your authentication
3. If not logged in → Redirects to login
4. If not admin role → Redirects to home page
5. If admin → Shows dashboard

### Connection Status

- 🟢 **Green**: Backend is connected and ready
- 🔴 **Red**: Backend is offline (check if server is running)

---

## 📊 Dashboard Overview

### Top Section: Business Analytics

**Row 1 - Booking Status**

```
Total Bookings     = All bookings in system right now
Pending Bookings   = Waiting for your confirmation
Completed          = Successfully delivered
Cancelled          = Customer cancelled or rejected
```

**Row 2 - Revenue & Time**

```
Estimated Revenue  = Money from completed bookings (AED)
Today's Bookings   = How many bookings came in today
This Week          = Bookings from last 7 days
Active Customers   = Different people who booked
```

### Middle Section: Business Insights

```
Most Popular Service = What service do customers want most?
Peak Booking Day      = Which day gets most bookings?
Average Booking Value = Average price of each completed job
```

---

## 🔍 Finding Bookings

### Method 1: Filter by Status

1. Click the **Status dropdown** above the table
2. Choose from:
   - "All Bookings" (see everything)
   - "Pending" (jobs to review)
   - "Confirmed" (in progress)
   - "Completed" (delivered)
   - "Cancelled" (rejected)
3. Table updates instantly

### Method 2: Search by Name or ID

1. Click the **Search box**
2. Type customer name or booking ID
3. Examples:
   - "Ahmad" → Shows all Ahmads
   - "123" → Shows booking #123
   - "john smith" → Shows exact match or partial

### Combine Both

Use filter AND search together:

- Filter: "Pending"
- Search: "Ahmad"
- Result: Only pending bookings from Ahmad

---

## ✅ Managing Bookings

### Pending Booking (Status: PENDING)

Shows 3 buttons:

```
[✓ Confirm]  [✓ Done]  [✕ Cancel]
```

**✓ Confirm**: Accept the job

- Click → Confirm dialog → Status changes to "Confirmed"
- Use when: You accept the booking

**✓ Done**: Complete the job

- Click → Job marked complete
- Revenue counted & added to total
- Use when: Laundry is done and delivered

**✕ Cancel**: Reject the job

- Click → Status changes to "Cancelled"
- Revenue NOT affected
- Use when: Customer cancels or you can't do it

### Confirmed Booking (Status: CONFIRMED)

Shows 2 buttons:

```
[✓ Done]  [✕ Cancel]
```

**✓ Done**: Complete the job
**✕ Cancel**: Cancel the job if needed

### Completed Booking (Status: COMPLETED)

No buttons - job is done, locked

### Cancelled Booking (Status: CANCELLED)

No buttons - job is cancelled, locked

---

## 💡 Quick Tips

### Tip 1: Check Today's Work

1. Look at **"Today's Bookings"** card
2. See the number
3. Filter by status → "Pending"
4. Work through all pending bookings

### Tip 2: Monitor Revenue

- **Estimated Revenue** only counts completed bookings
- It updates automatically when you mark jobs as "Done"
- This is your income from completed work

### Tip 3: Understand Customer Demand

- **Most Popular Service**: Promote this service in marketing
- **Peak Booking Day**: Schedule more staff for this day
- **Active Customers**: Know how many unique customers you have

### Tip 4: Quick Customer Lookup

- Manager calls: "Where's Ahmed's booking?"
- Search for "Ahmed" in search box
- Click one second, you see it

### Tip 5: Bulk Review

- Filter by "Pending"
- Shows only jobs waiting for you
- Go through one by one
- Confirm or cancel each

---

## 📱 Using on Mobile

### Mobile Layout

- Dropdowns stack vertically
- Still fully functional
- Table scrolls left/right
- All buttons are tappable

### Pro Tips for Mobile

1. Landscape mode easier for table
2. Tap buttons are large (easy to click)
3. Two-finger scroll for table
4. Filters still work exactly the same

---

## 🔄 Refreshing Data

### Automatic Refresh

- Dashboard auto-refreshes every 30 seconds
- No manual action needed
- Analytics update automatically

### Manual Refresh

- Click **"🔄 Refresh Data"** button in header
- Instantly fetches latest data
- Use if you want immediate update

---

## Understanding the Table

```
ID      = Booking number (#123)
Customer = Person's name
Phone   = Contact number
Service = Type of service (Express Wash, Dry Cleaning, etc.)
Qty     = Quantity in kg
Price   = Total cost (service price × quantity)
Status  = Current status (color-coded)
Date    = When booking was created
Actions = Buttons to update status
```

### Color-Coded Rows

- 🟨 **Yellow**: Pending (needs attention)
- 🟩 **Green**: Completed (done successfully)
- 🟥 **Red**: Cancelled (rejected)
- ⚪ **White**: Confirmed (in progress)

---

## Revenue Tracking

### How Revenue is Calculated

```
Revenue = SUM of (Price × Quantity) for all COMPLETED bookings

Example:
Booking 1: 5kg × AED 100/kg = AED 500 ✅ Completed
Booking 2: 3kg × AED 50/kg = AED 150 ✅ Completed
Booking 3: 2kg × AED 200/kg = AED 400 ❌ Pending (Not counted)

Total Revenue = AED 500 + AED 150 = AED 650
```

### When Revenue Updates

- Only when status changes to "Completed"
- Not when pending or confirmed
- Not if cancelled (exclusion)

### Checking Your Revenue

1. Look at **"Estimated Revenue"** card
2. This is your income from completed work
3. Mark jobs as "Done" to add to revenue

---

## Common Scenarios

### Scenario 1: Customer Calls to Cancel

**Steps:**

1. Search for customer name
2. Find their pending/confirmed booking
3. Click [✕ Cancel]
4. Confirm cancellation
5. Done - booking marked as cancelled
6. Revenue unaffected (if wasn't completed)

### Scenario 2: Job is Complete

**Steps:**

1. Filter by "Pending" or "Confirmed"
2. Find the job
3. Click [✓ Done]
4. Status changes to "Completed"
5. Amount added to "Estimated Revenue"

### Scenario 3: Accept a New Booking

**Steps:**

1. Check **"Today's Bookings"** number
2. Filter by status "Pending"
3. Review details
4. Click [✓ Confirm]
5. Status changes to "Confirmed"
6. Work on the job

### Scenario 4: Check Business Health

**Steps:**

1. Look at top cards:
   - Total bookings this week
   - Revenue earned this week
   - How many customers
2. Look at insights:
   - What's popular?
   - When's busiest?
3. Make business decisions

### Scenario 5: Find Specific Booking

**Steps:**

1. Click Search box
2. Type booking ID (123) OR customer name (Ahmed)
3. Instantly shows matching bookings
4. Click to view or take action

---

## Troubleshooting

### Problem: I see "Loading bookings..."

**Solution:** Wait 2-3 seconds, system is fetching data

### Problem: Status didn't change

**Solution:**

1. Click Refresh button
2. Wait for data to load
3. Check if you clicked confirm dialog

### Problem: Revenue still shows old number

**Solution:**

1. Mark jobs as "Done" (complete status)
2. Revenue updates automatically
3. Refresh if needed

### Problem: Search not finding customer

**Solution:**

1. Check if name is exact match
2. Try just first name
3. Try last name
4. Check spelling

### Problem: Mobile table looks squished

**Solution:**

1. Rotate phone to landscape
2. Table is easier to read sideways
3. Swipe left/right to scroll

---

## Best Practices

### ✅ Do This

- ✅ Refresh daily to see latest bookings
- ✅ Process pending jobs within 24 hours
- ✅ Mark jobs as "Done" when delivered (builds revenue)
- ✅ Use filter to focus on what needs doing
- ✅ Check "Most Popular Service" for marketing ideas
- ✅ Monitor revenue weekly for business health

### ❌ Don't Do This

- ❌ Delete bookings (they're never deleted - only status change)
- ❌ Ignore pending bookings for days
- ❌ Forget to mark jobs as "Done"
- ❌ Cancel bookings without customer approval
- ❌ Close browser without saving (auto-saves to database)

---

## Keyboard Shortcuts

- **Tab**: Move between fields
- **Enter**: Search or apply filter
- **Esc**: Cancel any dialog
- **F5**: Refresh page (or click refresh button)

---

## Need Help?

**Quick Reference**:

1. Check status and revenue in top cards
2. Use filter to narrow down what you see
3. Use search when looking for specific booking
4. Click action buttons to update status
5. Check insights for business trends

**Common Questions**:

**Q: Where's my revenue number?**
A: Look for "Estimated Revenue" card in green (top right section)

**Q: How do I find Ahmed's booking?**
A: Click search box, type "Ahmed", press Enter

**Q: What's the difference between Confirm and Done?**
A: Confirm = Accept job, Done = Deliver job (counts revenue)

**Q: Can I delete a booking?**
A: No, bookings are never deleted - only status changed to cancelled

**Q: Why isn't revenue showing?**
A: Only completed bookings count. Mark jobs as "Done" to add revenue.

---

## Your Dashboard Status

- **Current Time**: Check your system clock
- **Backend Status**: See green checkmark in header
- **Last Refresh**: Auto-refreshes every 30 seconds
- **Your Role**: Admin (see top analytics)

---

**💡 Pro Tip**: Bookmark admin.html and check it first thing every morning to see today's bookings!

**📊 Remember**: Your dashboard is your business control center. Use the analytics to make smart decisions about:

- Which services to promote
- When to schedule extra staff
- Your daily/weekly revenue
- Your customer base size

Good luck managing your laundry business! 🎉
