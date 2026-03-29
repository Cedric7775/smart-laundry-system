// ========== Device utilities ==========
const DeviceUtil = {
  isMobile: () =>
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent,
    ),
  isTablet: () => /iPad|Android(?!.*Mobile)|Tablet/i.test(navigator.userAgent),
  isTouchDevice: () =>
    "ontouchstart" in window ||
    navigator.maxTouchPoints > 0 ||
    navigator.msMaxTouchPoints > 0,
  isSmallScreen: () => window.innerWidth <= 768,
};

// ========== Authentication ==========
function updateAuthNav() {
  const token = localStorage.getItem("access_token");
  const authNav = document.getElementById("authNav");
  const dashboardNav = document.getElementById("dashboardNav");
  const profileDropdownNav = document.getElementById("profileDropdownNav");
  const logoutNav = document.getElementById("logoutNav");

  if (token && authNav && dashboardNav && profileDropdownNav) {
    authNav.style.display = "none";
    dashboardNav.style.display = "block";
    profileDropdownNav.style.display = "block";
    if (logoutNav) logoutNav.style.display = "none";

    // Load and display profile in dropdown
    loadProfileToDropdown();
  } else if (authNav) {
    authNav.style.display = "block";
    if (dashboardNav) dashboardNav.style.display = "none";
    if (profileDropdownNav) profileDropdownNav.style.display = "none";
    if (logoutNav) logoutNav.style.display = "none";
  }
}

async function loadProfileToDropdown() {
  try {
    const token = localStorage.getItem("access_token");
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    // Update dropdown button
    document.getElementById("profileDropdownName").textContent =
      user.name || "Profile";

    // Fetch full profile from API
    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      const profile = data.user;

      // Update dropdown content
      document.getElementById("profileDropdownTitle").textContent =
        profile.name || "Your Profile";
      document.getElementById("profileDropdownEmail").textContent =
        profile.email || "";
      document.getElementById("profileDropdownNameVal").textContent =
        profile.name || "-";
      document.getElementById("profileDropdownPhoneVal").textContent =
        profile.phone || "-";
      document.getElementById("profileDropdownAddressVal").textContent =
        profile.address || "Not set";

      // Format date
      if (profile.created_at) {
        const date = new Date(profile.created_at);
        document.getElementById("profileDropdownDateVal").textContent =
          date.toLocaleDateString();
      }
    }
  } catch (err) {
    console.error("Error loading profile:", err);
  }
}

function toggleProfileDropdown() {
  const menu = document.getElementById("profileDropdownMenu");
  const btn = document.getElementById("profileDropdownBtn");

  if (menu && btn) {
    menu.classList.toggle("active");
    btn.classList.toggle("active");
  }
}

// Close dropdown when clicking outside
document.addEventListener("click", (event) => {
  const dropdown = document.getElementById("profileDropdownNav");
  const menu = document.getElementById("profileDropdownMenu");
  const btn = document.getElementById("profileDropdownBtn");

  if (dropdown && !dropdown.contains(event.target)) {
    menu?.classList.remove("active");
    btn?.classList.remove("active");
  }
});

function logoutFromNav() {
  if (confirm("Are you sure you want to logout?")) {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    updateAuthNav();
    alert("Logged out successfully");
  }
}

// Update auth nav on page load
window.addEventListener("load", () => {
  updateAuthNav();
});

// ========== Modal controls ==========
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

  // Initialize form validation
  setupFieldValidation();

  // Initialize price display
  updatePrice();
}

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

  // Also close confirmation and success modals
  document.getElementById("confirmationModal").style.display = "none";
  document.getElementById("successModal").style.display = "none";
}

window.addEventListener("click", (event) => {
  const modal = document.getElementById("modal");
  const confirmationModal = document.getElementById("confirmationModal");
  const successModal = document.getElementById("successModal");

  if (modal && event.target === modal) closeForm();
  if (confirmationModal && event.target === confirmationModal)
    closeConfirmation();
  if (successModal && event.target === successModal) closeSuccess();
});

// ========== API ==========
// Dynamic API URL - works for both local dev and production
const API_BASE_URL =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://localhost:5000/api"
    : `${window.location.protocol}//${window.location.host}/api`;

const BookingAPI = {
  async create(bookingData) {
    const response = await fetch(`${API_BASE_URL}/bookings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bookingData),
    });
    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    return await response.json();
  },

  async getAll() {
    const response = await fetch(`${API_BASE_URL}/bookings`);
    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    return await response.json();
  },

  async getById(id) {
    const response = await fetch(`${API_BASE_URL}/bookings/${id}`);
    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    return await response.json();
  },

  async updateStatus(id, status) {
    const response = await fetch(`${API_BASE_URL}/bookings/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    if (!response.ok) throw new Error(`API error: ${response.statusText}`);
    return await response.json();
  },
};

function resolveServiceName(str) {
  if (!str) return "";
  return str.trim();
}

function selectService(serviceName) {
  const service = resolveServiceName(serviceName);
  const serviceInput = document.getElementById("service");
  if (serviceInput) {
    const foundOption = Array.from(serviceInput.options).find(
      (opt) =>
        opt.value.toLowerCase().includes(service.toLowerCase()) ||
        opt.textContent.toLowerCase().includes(service.toLowerCase()),
    );
    if (foundOption) serviceInput.value = foundOption.value;
    else serviceInput.value = service;
  }

  localStorage.setItem(
    "selectedService",
    JSON.stringify({ service, timestamp: new Date().toISOString() }),
  );
  openForm();
}

function selectBundle(bundleKey) {
  const map = {
    mini: "Mini Pack - 5 items - KES 250",
    standard: "Standard Pack - 10 items - KES 450",
    family: "Family Pack - 20 items - KES 800",
  };

  const selected = map[bundleKey] || bundleKey;
  alert(`✅ Selected ${selected}. Continue to booking.`);
  selectService(selected);
}

function filterServices(category, event) {
  const cards = document.querySelectorAll(".service-card");
  const buttons = document.querySelectorAll(".category-btn");
  buttons.forEach((btn) => btn.classList.remove("active"));
  if (event && event.currentTarget) event.currentTarget.classList.add("active");

  cards.forEach((card) => {
    const matches = category === "all" || card.dataset.category === category;
    card.style.display = matches ? "flex" : "none";
    card.style.opacity = matches ? "1" : "0";
  });

  localStorage.setItem("selectedServiceCategory", category);
}

// ========== Form State ==========
let isSubmittingBooking = false;
let isSubmittingMessage = false;

// ========== Validation ==========
function validateBookingForm() {
  const name = document.getElementById("name")?.value.trim() || "";
  const phone = document.getElementById("phone")?.value.trim() || "";
  const location = document.getElementById("location")?.value.trim() || "";
  const service = document.getElementById("service")?.value || "";
  const delivery_date = document.getElementById("delivery_date")?.value || "";
  const quantity = Number(document.getElementById("quantity")?.value || "0");

  if (!name || name.length < 2) return "Name must be at least 2 characters.";
  if (!phone || phone.length < 9) return "Phone must be at least 9 characters.";
  if (!location || location.length < 3)
    return "Location must be at least 3 characters.";
  if (!service) return "Please select a service.";
  if (quantity < 1 || quantity > 100)
    return "Quantity must be between 1 and 100 kg.";
  if (!delivery_date) return "Please select a delivery date.";

  return null; // Valid
}

function validateContactForm() {
  const name = document.getElementById("contact-name")?.value.trim() || "";
  const phone = document.getElementById("contact-phone")?.value.trim() || "";
  const email = document.getElementById("contact-email")?.value.trim() || "";
  const service = document.getElementById("contact-service")?.value || "";
  const message =
    document.getElementById("contact-message")?.value.trim() || "";

  if (!name || name.length < 2) return "Name must be at least 2 characters.";
  if (!phone || phone.length < 9) return "Phone must be at least 9 characters.";
  if (!email || !email.includes("@"))
    return "Please enter a valid email address.";
  if (!service) return "Please select a service.";
  if (!message || message.length < 10)
    return "Message must be at least 10 characters.";

  return null; // Valid
}

async function sendWhatsApp() {
  // Prevent duplicate submissions
  if (isSubmittingBooking) return;

  // Validate form
  const validationError = validateBookingForm();
  if (validationError) {
    alert(`❌ ${validationError}`);
    return;
  }

  const submitBtn = event?.target;
  const name = document.getElementById("name").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const location = document.getElementById("location").value.trim();
  const service = document.getElementById("service").value;
  const quantity = Number(document.getElementById("quantity").value);
  const delivery_date = document.getElementById("delivery_date").value;

  let pricePerKg = 5;
  const svc = service.toLowerCase();
  if (svc.includes("premium")) pricePerKg = 800;
  if (svc.includes("dry")) pricePerKg = 100;
  if (svc.includes("carpet")) pricePerKg = 1200;
  if (svc.includes("wedding")) pricePerKg = 1500;
  if (svc.includes("express")) pricePerKg = 1100;

  const totalPrice = (quantity * pricePerKg).toFixed(2);

  // Set loading state
  isSubmittingBooking = true;
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.style.opacity = "0.6";
    submitBtn.textContent = "⏳ Processing...";
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

    alert(
      `✅ Success!\n\nBooking ID: #${booking.booking_id || "Created"}\nService: ${service}\nDate: ${delivery_date}\n\nWe'll contact you shortly.`,
    );

    closeForm();
    ["name", "phone", "location", "service", "delivery_date"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.value = "";
    });
    const qty = document.getElementById("quantity");
    if (qty) qty.value = "1";
    localStorage.removeItem("selectedService");
  } catch (err) {
    console.error("Booking error:", err);
    alert(
      `❌ Booking Failed\n\n${err.message}\n\nPlease try again or contact us directly.`,
    );
  } finally {
    // Reset loading state
    isSubmittingBooking = false;
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.style.opacity = "1";
      submitBtn.textContent = "✓ Book Now";
    }
  }
}

// ========== PRICE CALCULATION ==========
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

function getServicePrice(serviceName) {
  if (!serviceName) return 50;
  const name = serviceName.toLowerCase();
  return SERVICE_PRICES[name] || 50;
}

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

// ========== FORM VALIDATION ==========
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

// Add real-time validation
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

// ========== BOOKING FLOW ==========
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

  // Populate confirmation modal
  const name = document.getElementById("name").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const service = document.getElementById("service").value;
  const quantity = Number(document.getElementById("quantity").value);
  const location = document.getElementById("location").value.trim();
  const delivery_date = document.getElementById("delivery_date").value;
  const pricePerKg = getServicePrice(service);
  const totalPrice = quantity * pricePerKg;

  // Format date
  const dateObj = new Date(delivery_date);
  const formattedDate = dateObj.toLocaleDateString("en-US", {
    weekday: "short",
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  document.getElementById("confirmService").textContent = service;
  document.getElementById("confirmQuantity").textContent = `${quantity} kg`;
  document.getElementById("confirmLocation").textContent = location;
  document.getElementById("confirmDate").textContent = formattedDate;
  document.getElementById("confirmPhone").textContent = phone;
  document.getElementById("confirmTotal").textContent =
    `AED ${totalPrice.toLocaleString()}`;

  // Show confirmation modal, hide booking form
  document.getElementById("modal").style.display = "none";
  document.getElementById("confirmationModal").style.display = "flex";
}

async function submitBooking() {
  if (isSubmittingBooking) return;

  const submitBtn = event?.target;
  const name = document.getElementById("name").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const service = document.getElementById("service").value;
  const quantity = Number(document.getElementById("quantity").value);
  const location = document.getElementById("location").value.trim();
  const delivery_date = document.getElementById("delivery_date").value;
  const pricePerKg = getServicePrice(service);
  const totalPrice = quantity * pricePerKg;

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

    // Show success modal
    showSuccess(booking, service, totalPrice);

    // Close confirmation modal
    closeConfirmation();

    // Reset form
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
    isSubmittingBooking = false;
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.style.opacity = "1";
      submitBtn.textContent = "✓ Confirm & Book";
    }
  }
}

function showSuccess(booking, service, totalPrice) {
  document.getElementById("successBookingId").textContent =
    `#${booking.booking_id || "12345"}`;
  document.getElementById("successService").textContent = service;
  document.getElementById("successPrice").textContent =
    `AED ${totalPrice.toLocaleString()}`;

  document.getElementById("confirmationModal").style.display = "none";
  document.getElementById("successModal").style.display = "flex";
}

function closeConfirmation() {
  document.getElementById("confirmationModal").style.display = "none";
  document.getElementById("modal").style.display = "flex";
}

function closeSuccess() {
  document.getElementById("successModal").style.display = "none";
  closeForm();
}

function goToDashboard() {
  const token = localStorage.getItem("access_token");
  if (token) {
    window.location.href = "/dashboard.html";
  } else {
    alert("Please log in to view your bookings");
    window.location.href = "/auth.html";
  }
}

function applySavedPreferences() {
  // Don't auto-open form on page load - just restore the filter category if exists
  const savedCat = localStorage.getItem("selectedServiceCategory");
  if (savedCat) filterServices(savedCat);

  // Don't restore selectedService on init - it opens the booking form unwantedly
  // Users can select services manually from the page
}

function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (e) => {
      const href = anchor.getAttribute("href");
      if (href === "#") return;
      e.preventDefault();
      const target = document.querySelector(href);
      if (!target) return;
      const headerOffset = DeviceUtil.isMobile() ? 70 : 60;
      const topPos =
        target.getBoundingClientRect().top + window.pageYOffset - headerOffset;
      window.scrollTo({ top: topPos, behavior: "smooth" });
    });
  });
}

function initCardToggles() {
  document.querySelectorAll(".pricing-card, .step-card").forEach((card) => {
    card.addEventListener("click", () => {
      card.classList.toggle("expanded");
      const label = card.querySelector(".toggle-label");
      if (label)
        label.textContent = card.classList.contains("expanded")
          ? "Show less"
          : "Show more";
    });
  });
}

function initTurnaroundAnimation() {
  const section = document.getElementById("turnaround");
  if (!section || !window.IntersectionObserver) return;
  new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) section.classList.add("animate-in");
      });
    },
    { threshold: 0.25 },
  ).observe(section);
}

async function sendMessage() {
  // Prevent duplicate submissions
  if (isSubmittingMessage) return;

  // Validate form
  const validationError = validateContactForm();
  if (validationError) {
    alert(`❌ ${validationError}`);
    return;
  }

  const submitBtn = event?.target;
  const name = document.getElementById("contact-name").value.trim();
  const phone = document.getElementById("contact-phone").value.trim();
  const email = document.getElementById("contact-email").value.trim();
  const service = document.getElementById("contact-service").value;
  const message = document.getElementById("contact-message").value.trim();

  // Set loading state
  isSubmittingMessage = true;
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.style.opacity = "0.6";
    submitBtn.textContent = "⏳ Sending...";
  }

  try {
    const response = await fetch(`${API_BASE_URL}/contacts/send-email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, phone, email, service, message }),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Failed to send message");
    }

    alert(
      `✅ Message Sent Successfully!\n\nWe've received your message and will reply to ${email} within 24 hours.`,
    );

    // Clear form
    document.getElementById("contact-name").value = "";
    document.getElementById("contact-phone").value = "";
    document.getElementById("contact-email").value = "";
    document.getElementById("contact-service").value = "";
    document.getElementById("contact-message").value = "";
  } catch (err) {
    console.error("Message send failed:", err);
    alert(
      `❌ Failed to Send Message\n\n${err.message}\n\nPlease try again or call us directly.`,
    );
  } finally {
    // Reset loading state
    isSubmittingMessage = false;
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.style.opacity = "1";
      submitBtn.textContent = "📩 Send Message";
    }
  }
}

function initPage() {
  // Scroll to top on page load
  window.scrollTo(0, 0);
  document.body.scrollTop = 0; // For older browsers

  // Ensure modal is hidden with !important priority
  const modal = document.getElementById("modal");
  if (modal) {
    modal.style.setProperty("display", "none", "important");
    modal.classList.remove("fadeIn");
    modal.classList.remove("fadeOut");
    document.body.style.overflow = "auto";
  }

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeForm();
  });
  initSmoothScroll();
  initCardToggles();
  initTurnaroundAnimation();
  applySavedPreferences();
  console.log("✅ Page initialized");
}

window.addEventListener("DOMContentLoaded", initPage);
