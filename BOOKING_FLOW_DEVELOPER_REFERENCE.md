# 💻 Booking Flow - Developer Reference

## Function Map & Architecture

### Price Calculation System

#### `SERVICE_PRICES` Object

```javascript
const SERVICE_PRICES = {
  "express wash": 1100,
  "premium care": 800,
  "dry cleaning": 100,
  "ironing & folding": 50,
  "bed linen": 75,
  "carpet cleaning": 1200,
  "bulk service": 50,
  "wedding collection": 1500,
};
```

**Purpose**: Master price mapping for all services (AED per kg)

---

#### `getServicePrice(serviceName)` → `number`

```javascript
function getServicePrice(serviceName) {
  if (!serviceName) return 50;
  const name = serviceName.toLowerCase();
  return SERVICE_PRICES[name] || 50;
}
```

**Purpose**: Lookup price for a given service name  
**Returns**: Price per kg (defaults to 50 if not found)  
**Usage**: Called by `updatePrice()` and `reviewBooking()`

---

#### `updatePrice()` → `void`

```javascript
function updatePrice() {
  const service = document.getElementById("service")?.value || "";
  const quantity = Number(document.getElementById("quantity")?.value || 1);

  if (!service) {
    document.getElementById("servicePrice").textContent = "AED 0.00";
    document.getElementById("quantityDisplay").textContent = quantity + " kg";
    document.getElementById("totalPrice").textContent = "AED 0.00";
    return;
  }

  const pricePerKg = getServicePrice(service);
  const totalPrice = quantity * pricePerKg;

  document.getElementById("servicePrice").textContent =
    `AED ${pricePerKg.toLocaleString()}`;
  document.getElementById("quantityDisplay").textContent = `${quantity} kg`;
  document.getElementById("totalPrice").textContent =
    `AED ${totalPrice.toLocaleString()}`;
}
```

**Purpose**: Update price display in real-time  
**Triggered**: `onchange` on service select, `oninput`/`onchange` on quantity  
**Updates**: Three elements:

- `servicePrice`: Unit price (e.g., "AED 1,100")
- `quantityDisplay`: Quantity (e.g., "5 kg")
- `totalPrice`: Total (e.g., "AED 5,500")

---

### Form Validation System

#### `validateField(fieldId, errorId)` → `boolean`

```javascript
function validateField(fieldId, errorId) {
  const field = document.getElementById(fieldId);
  const errorMsg = document.getElementById(errorId);

  if (!field || !errorMsg) return true;

  field.classList.remove("input-error");
  errorMsg.classList.remove("show");
  errorMsg.textContent = "";

  let error = null;

  switch (fieldId) {
    case "name":
      const name = field.value.trim();
      if (!name || name.length < 2)
        error = "Name must be at least 2 characters";
      break;
    case "phone":
      const phone = field.value.trim();
      if (!phone || phone.length < 9)
        error = "Phone must be at least 9 characters";
      break;
    case "location":
      const location = field.value.trim();
      if (!location || location.length < 3)
        error = "Location must be at least 3 characters";
      break;
    case "service":
      if (!field.value) error = "Please select a service";
      break;
    case "quantity":
      const qty = Number(field.value);
      if (qty < 1 || qty > 100) error = "Quantity must be between 1-100 kg";
      break;
    case "delivery_date":
      if (!field.value) error = "Please select a delivery date";
      break;
  }

  if (error) {
    field.classList.add("input-error");
    errorMsg.textContent = error;
    errorMsg.classList.add("show");
    return false;
  }
  return true;
}
```

**Purpose**: Validate individual form field and display error if invalid  
**Parameters**:

- `fieldId`: HTML element ID (e.g., "name")
- `errorId`: HTML element ID for error message (e.g., "error-name")
  **Returns**: `true` if valid, `false` if invalid  
  **Side Effects**:
- Adds/removes "input-error" CSS class
- Shows/hides error message
- Returns validation result

**Validation Rules**:
| Field | Rule |
|-------|------|
| name | Min 2 characters |
| phone | Min 9 characters |
| location | Min 3 characters |
| service | Must be selected |
| quantity | 1-100 kg |
| delivery_date | Must be selected |

---

#### `setupFieldValidation()` → `void`

```javascript
function setupFieldValidation() {
  ["name", "phone", "location", "service", "quantity", "delivery_date"].forEach(
    (fieldId) => {
      const field = document.getElementById(fieldId);
      if (field) {
        field.addEventListener("blur", () =>
          validateField(fieldId, `error-${fieldId}`),
        );
        field.addEventListener("change", () =>
          validateField(fieldId, `error-${fieldId}`),
        );
      }
    },
  );
}
```

**Purpose**: Attach validation listeners to all form fields  
**When Called**: In `openForm()` when booking modal opens  
**Listeners Added**:

- `blur` event: Validate when user leaves field
- `change` event: Validate when user changes value

---

### Booking Flow Functions

#### `reviewBooking()` → `void`

```javascript
function reviewBooking() {
  // Validate all fields
  let isValid = true;
  ["name", "phone", "location", "service", "quantity", "delivery_date"].forEach(
    (fieldId) => {
      if (!validateField(fieldId, `error-${fieldId}`)) {
        isValid = false;
      }
    },
  );

  if (!isValid) return;

  // Collect form data
  const name = document.getElementById("name").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const service = document.getElementById("service").value;
  const quantity = Number(document.getElementById("quantity").value);
  const location = document.getElementById("location").value.trim();
  const delivery_date = document.getElementById("delivery_date").value;
  const pricePerKg = getServicePrice(service);
  const totalPrice = quantity * pricePerKg;

  // Format delivery date
  const dateObj = new Date(delivery_date);
  const formattedDate = dateObj.toLocaleDateString("en-US", {
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  // Populate confirmation modal with data
  document.getElementById("confirmService").textContent = service;
  document.getElementById("confirmQuantity").textContent = `${quantity} kg`;
  document.getElementById("confirmLocation").textContent = location;
  document.getElementById("confirmDate").textContent = formattedDate;
  document.getElementById("confirmPhone").textContent = phone;
  document.getElementById("confirmTotal").textContent =
    `AED ${totalPrice.toLocaleString()}`;

  // Transition to confirmation modal
  document.getElementById("modal").style.display = "none";
  document.getElementById("confirmationModal").style.display = "flex";
}
```

**Purpose**: Validate all form fields and show confirmation modal  
**Flow**:

1. Validate all required fields
2. If any invalid, show errors and stop
3. If all valid, populate confirmation modal
4. Hide booking form, show confirmation modal
   **Confirmation Modal Values**:

- Service: From select dropdown
- Quantity: With "kg" unit
- Location: From location input
- Date: Formatted as "Mon, Mar 29, 2026"
- Phone: For confirmation message
- Total: Calculated from price × quantity

---

#### `submitBooking()` → `Promise<void>` (async)

```javascript
async function submitBooking() {
  if (isSubmittingBooking) return; // Prevent double-submit

  const submitBtn = event?.target;

  // Collect booking data
  const name = document.getElementById("name").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const service = document.getElementById("service").value;
  const quantity = Number(document.getElementById("quantity").value);
  const location = document.getElementById("location").value.trim();
  const delivery_date = document.getElementById("delivery_date").value;
  const pricePerKg = getServicePrice(service);
  const totalPrice = quantity * pricePerKg;

  // Set loading state
  isSubmittingBooking = true;
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.style.opacity = "0.6";
    submitBtn.textContent = "⏳ Confirming...";
  }

  try {
    const booking = await BookingAPI.create({
      name,
      phone,
      location,
      service,
      quantity,
      price: Number(totalPrice),
      delivery_date,
    });

    // Show success modal with booking details
    showSuccess(booking, service, totalPrice);

    // Close confirmation modal
    closeConfirmation();

    // Reset form for next booking
    ["name", "phone", "location", "service", "delivery_date"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.value = "";
    });
    const qty = document.getElementById("quantity");
    if (qty) qty.value = "1";
    updatePrice();
    localStorage.removeItem("selectedService");
  } catch (err) {
    console.error("Booking error:", err);
    alert(`❌ Booking Failed\n\n${err.message}\n\nPlease try again.`);
  } finally {
    // Reset button state
    isSubmittingBooking = false;
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.style.opacity = "1";
      submitBtn.textContent = "✓ Confirm & Book";
    }
  }
}
```

**Purpose**: Submit booking to API and show success  
**Flow**:

1. Prevent double submissions with `isSubmittingBooking` flag
2. Collect all booking data
3. Set button to loading state
4. Call `BookingAPI.create()` with booking data
5. On success, show success modal and reset form
6. On error, show error alert
7. Finally, reset button state
   **Loading State**: Button text changes to "⏳ Confirming..."  
   **Form Reset**: After success, all fields cleared for next booking

---

#### `showSuccess(booking, service, totalPrice)` → `void`

```javascript
function showSuccess(booking, service, totalPrice) {
  document.getElementById("successBookingId").textContent =
    `#${booking.booking_id || "12345"}`;
  document.getElementById("successService").textContent = service;
  document.getElementById("successPrice").textContent =
    `AED ${totalPrice.toLocaleString()}`;

  document.getElementById("confirmationModal").style.display = "none";
  document.getElementById("successModal").style.display = "flex";
}
```

**Purpose**: Display success modal with booking details  
**Parameters**:

- `booking`: Response object from API (contains `booking_id`)
- `service`: Service name (e.g., "Express Wash")
- `totalPrice`: Total price in AED (number)
  **Displays**:
- Booking ID: `#${booking.booking_id}`
- Service: User-friendly service name
- Price: Formatted with commas (e.g., "AED 5,500")

---

### Modal Control Functions

#### `closeConfirmation()` → `void`

```javascript
function closeConfirmation() {
  document.getElementById("confirmationModal").style.display = "none";
  document.getElementById("modal").style.display = "flex";
}
```

**Purpose**: Close confirmation modal and return to booking form  
**Usage**: "← Back" button on confirmation modal  
**Note**: Form data is preserved when returning

---

#### `closeSuccess()` → `void`

```javascript
function closeSuccess() {
  document.getElementById("successModal").style.display = "none";
  closeForm();
}
```

**Purpose**: Close success modal and booking form  
**Usage**: "✓ Done" button on success modal

---

#### `goToDashboard()` → `void`

```javascript
function goToDashboard() {
  const token = localStorage.getItem("access_token");
  if (token) {
    window.location.href = "/dashboard.html";
  } else {
    alert("Please log in to view your bookings");
    window.location.href = "/auth.html";
  }
}
```

**Purpose**: Navigate to dashboard or login page  
**Logic**:

- If user is logged in (has token): Go to `/dashboard.html`
- If not logged in: Show message and go to `/auth.html`
  **Usage**: "📊 View My Bookings" button on success modal

---

### Enhanced Modal Controls

#### Updated `openForm()` → `void`

```javascript
function openForm() {
  const bookingForm = document.getElementById("bookingForm");
  if (bookingForm) bookingForm.style.display = "block";

  const modal = document.getElementById("modal");
  if (!modal) return;
  modal.style.display = "flex";
  modal.classList.remove("fadeOut");
  modal.classList.add("fadeIn");
  document.body.style.overflow = "hidden";

  const deliveryDateInput = document.getElementById("delivery_date");
  if (deliveryDateInput) {
    const today = new Date().toISOString().split("T")[0];
    deliveryDateInput.min = today;
  }

  // NEW: Initialize form validation
  setupFieldValidation();

  // NEW: Initialize price display
  updatePrice();
}
```

**Changes**:

- Calls `setupFieldValidation()` to attach listeners
- Calls `updatePrice()` to show initial price

---

#### Updated `closeForm()` → `void`

```javascript
function closeForm() {
  const modal = document.getElementById("modal");
  if (!modal) return;
  modal.classList.remove("fadeIn");
  modal.classList.add("fadeOut");
  setTimeout(() => {
    modal.style.display = "none";
    modal.classList.remove("fadeOut");
    document.body.style.overflow = "auto";
  }, 250);

  // NEW: Also close confirmation and success modals
  document.getElementById("confirmationModal").style.display = "none";
  document.getElementById("successModal").style.display = "none";
}
```

**Changes**:

- Also closes confirmation and success modals
- Ensures clean state when form is closed

---

#### Updated Event Listeners

```javascript
window.addEventListener("click", (event) => {
  const modal = document.getElementById("modal");
  const confirmationModal = document.getElementById("confirmationModal");
  const successModal = document.getElementById("successModal");

  if (modal && event.target === modal) closeForm();
  if (confirmationModal && event.target === confirmationModal)
    closeConfirmation();
  if (successModal && event.target === successModal) closeSuccess();
});
```

**Purpose**: Close modals when clicking outside them  
**Covers**: All three modals (booking, confirmation, success)

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│ User visits index.html                              │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓
        ┌─────────────────────┐
        │ Clicks "Book Now"   │
        └────────┬────────────┘
                 │
                 ↓
        ┌───────────────────────────┐
        │ openForm()                │
        │ - Show booking modal      │
        │ - setupFieldValidation()  │
        │ - updatePrice()           │
        └────────┬──────────────────┘
                 │
                 ↓
        ┌──────────────────────┐
        │ User fills form      │
        │ - Real-time price    │
        │ - On-blur validation │
        └────────┬─────────────┘
                 │
                 ↓
        ┌──────────────────────┐
        │ Click "Review Booking"
        └────────┬─────────────┘
                 │
                 ↓
        ┌──────────────────────┐
        │ reviewBooking()      │
        │ - Validate all fields│
        │ - If invalid: ❌     │
        │ - If valid:          │
        │   - Populate confirm │
        │   - Show confirm     │
        └────────┬─────────────┘
                 │
                 ├─ Error? → Show error messages ↻
                 │
                 ↓
        ┌──────────────────────┐
        │ Confirmation Modal   │
        │ - Review summary     │
        │ - Confirm price      │
        └────────┬─────────────┘
                 │
         ┌───────┴───────┐
         ↓               ↓
    "Back"           "Confirm"
         │               │
         ↓               ↓
    Return to        submitBooking()
    form (data        - POST to API
    preserved)       - Show loading
                     - On success:
                       - showSuccess()
                       - Reset form
                     - On error:
                       - Show alert
                 │
                 ↓
        ┌──────────────────────┐
        │ Success Modal        │
        │ - Show booking ID    │
        │ - Show service info  │
        │ - Show total price   │
        └────────┬─────────────┘
                 │
         ┌───────┴──────────┐
         ↓                  ↓
    "View Bookings"    "Done"
         │                  │
         ↓                  ↓
    closeSuccess()     closeSuccess()
    + goToDashboard()   + closeForm()
         │                  │
         ↓                  ↓
    Navigate to         Close all
    dashboard or        modals
    login page          Back to
                        main page
```

---

## State Variables

```javascript
let isSubmittingBooking = false; // Prevents double-submission on confirmation
let isSubmittingMessage = false; // For contact form (separate)
```

**Purpose**: Prevent duplicate API calls

---

## CSS Classes for Styling

### Error Display

- `.error-message`: Error text (hidden by default)
- `.error-message.show`: Show error message
- `.input-error`: Red border + light red background on invalid input

### Form Sections

- `.form-section`: Grouped section (gray background, purple border)
- `.section-title`: Section heading (uppercase, bold)

### Price Display

- `.price-summary`: Price box (gradient background)
- `.price-row`: Single price item (service, quantity)
- `.price-row-total`: Total price (bold, large)

### Modals

- `.modal`: Base modal (appears as flex overlay)
- `.modal-content`: Modal container
- `.confirmation-content`: Confirmation modal specific
- `.success-content`: Success modal specific

### Buttons

- `.btn-primary`: Main action button (purple gradient)
- `.btn-secondary`: Secondary/cancel button (gray)

---

## Integration Points

### Required HTML Elements

```html
<!-- Booking Form -->
<input id="name" id="phone" id="location" id="delivery_date" />
<select id="service" id="quantity" />
<span id="error-{fieldId}" />
<!-- For each field -->
<span id="servicePrice" id="quantityDisplay" id="totalPrice" />

<!-- Confirmation Modal -->
<div id="confirmationModal">
  <span
    id="confirmService"
    id="confirmQuantity"
    id="confirmLocation"
    id="confirmDate"
    id="confirmPhone"
    id="confirmTotal"
  />
</div>

<!-- Success Modal -->
<div id="successModal">
  <span id="successBookingId" id="successService" id="successPrice" />
</div>
```

### Required API

- `BookingAPI.create(bookingData)`: Submits booking to backend

### Required Styles

- Modal styling (defined in styles.css)
- Form section styling
- Error styling
- Button styling

---

## Performance Considerations

1. **Price calculation**: Uses `toLocaleString()` for formatting (O(n) where n = digits)
2. **Validation**: Simple string checks (O(1) per field)
3. **DOM updates**: Targeted updates using `getElementById()` (O(1))
4. **Event listeners**: Attached once in `setupFieldValidation()` at form open
5. **API calls**: Async, with loading state to prevent duplicate submissions

---

## Future Enhancements

Possible additions:

- [ ] Service add-ons (e.g., "Urgent delivery" +AED 50)
- [ ] Coupon code validation
- [ ] Pickup time selection
- [ ] Special instructions textarea
- [ ] Save booking for later
- [ ] Address book integration
- [ ] SMS/Email confirmation
- [ ] Real-time tracking updates
