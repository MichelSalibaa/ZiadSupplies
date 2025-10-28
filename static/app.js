const FALLBACK_CATEGORY_IMAGE = "/static/images/category-detergent.svg";
const FALLBACK_PRODUCT_IMAGE = "/static/images/product-microfiber.svg";

const state = {
    products: new Map(),
    cart: new Map(),
};

document.addEventListener("DOMContentLoaded", () => {
    fetchCatalog();
    bindCheckoutForm();
    const yearEl = document.getElementById("year");
    if (yearEl) {
        yearEl.textContent = new Date().getFullYear();
    }
});

async function fetchCatalog() {
    const grid = document.getElementById("catalog-grid");
    if (!grid) return;

    try {
        const response = await fetch("/api/catalog");
        if (!response.ok) {
            throw new Error("Unable to load catalog");
        }
        const data = await response.json();
        renderCatalog(data.categories || []);
    } catch (error) {
        grid.innerHTML = `<p class="form-messages error">${error.message}</p>`;
    }
}

function renderCatalog(categories) {
    const grid = document.getElementById("catalog-grid");
    if (!grid) return;

    grid.innerHTML = "";
    if (!categories.length) {
        grid.innerHTML = "<p class=\"form-messages\">Catalog is being prepared. Please check back soon.</p>";
        return;
    }

    categories.forEach((category) => {
        const card = document.createElement("article");
        card.className = "category-card";

        const imageWrapper = document.createElement("div");
        imageWrapper.className = "category-image";
        const image = document.createElement("img");
        image.src = category.imageUrl || FALLBACK_CATEGORY_IMAGE;
        image.alt = category.name;
        imageWrapper.appendChild(image);

        card.appendChild(imageWrapper);

        const body = document.createElement("div");
        body.className = "category-body";

        const title = document.createElement("h3");
        title.textContent = category.name;
        body.appendChild(title);

        const description = document.createElement("p");
        description.textContent = category.description || "";
        body.appendChild(description);

        const toggle = document.createElement("button");
        toggle.className = "category-toggle";
        toggle.type = "button";
        toggle.textContent = "View items";
        toggle.setAttribute("aria-expanded", "false");
        body.appendChild(toggle);

        card.appendChild(body);

        const subcategories = category.subcategories || [];
        const totalItems = subcategories.reduce(
            (count, group) => count + ((group.items && group.items.length) || 0),
            0
        );

        const label = document.createElement("span");
        label.className = "category-label";
        label.textContent = `${subcategories.length} groups • ${totalItems} items`;
        imageWrapper.appendChild(label);

        const itemsContainer = document.createElement("div");
        itemsContainer.className = "category-items";
        itemsContainer.hidden = true;

        subcategories.forEach((subcategory) => {
            const section = document.createElement("section");
            section.className = "subcategory";

            const heading = document.createElement("h4");
            heading.textContent = subcategory.subcategory;
            section.appendChild(heading);

            const productList = document.createElement("div");
            productList.className = "subcategory-items";

            (subcategory.items || []).forEach((product) => {
                state.products.set(product.id, {
                    ...product,
                    category: category.name,
                    subcategory: subcategory.subcategory,
                });

                const productCard = document.createElement("article");
                productCard.className = "product-card";

                const productImage = document.createElement("img");
                productImage.className = "product-image";
                productImage.src = product.imageUrl || FALLBACK_PRODUCT_IMAGE;
                productImage.alt = product.name;
                productCard.appendChild(productImage);

                const info = document.createElement("div");
                info.className = "product-info";

                const nameEl = document.createElement("strong");
                nameEl.textContent = product.name;
                info.appendChild(nameEl);

                const meta = document.createElement("div");
                meta.className = "product-meta";
                const priceText = `$${Number(product.price).toFixed(2)}`;
                if (product.unit) {
                    meta.appendChild(document.createElement("span")).textContent = product.unit;
                }
                meta.appendChild(document.createElement("span")).textContent = priceText;
                meta.appendChild(document.createElement("span")).textContent = subcategory.subcategory;
                info.appendChild(meta);

                if (product.description) {
                    const desc = document.createElement("p");
                    desc.textContent = product.description;
                    info.appendChild(desc);
                }

                const actions = document.createElement("div");
                actions.className = "product-actions";

                const quantityInput = document.createElement("input");
                quantityInput.type = "number";
                quantityInput.min = "1";
                quantityInput.value = "1";

                const addButton = document.createElement("button");
                addButton.className = "add-button";
                addButton.type = "button";
                addButton.textContent = "Add";
                addButton.addEventListener("click", () => {
                    const quantity = Math.max(1, parseInt(quantityInput.value, 10) || 1);
                    addToCart(product.id, quantity);
                    quantityInput.value = "1";
                });

                actions.appendChild(quantityInput);
                actions.appendChild(addButton);
                info.appendChild(actions);

                productCard.appendChild(info);
                productList.appendChild(productCard);
            });

            section.appendChild(productList);
            itemsContainer.appendChild(section);
        });

        toggle.addEventListener("click", () => {
            const expanded = itemsContainer.hidden;
            itemsContainer.hidden = !expanded;
            card.classList.toggle("expanded", expanded);
            toggle.setAttribute("aria-expanded", String(expanded));
            toggle.textContent = expanded ? "Hide items" : "View items";
        });

        card.appendChild(itemsContainer);
        grid.appendChild(card);
    });
}

function addToCart(productId, quantity) {
    const product = state.products.get(productId);
    if (!product) return;

    const existing = state.cart.get(productId) || { product, quantity: 0 };
    existing.quantity += quantity;
    state.cart.set(productId, existing);
    renderCart();
}

function removeFromCart(productId) {
    state.cart.delete(productId);
    renderCart();
}

function updateCartQuantity(productId, quantity) {
    const item = state.cart.get(productId);
    if (!item) return;

    const newQuantity = Math.max(1, quantity);
    item.quantity = newQuantity;
    state.cart.set(productId, item);
    renderCart();
}

function renderCart() {
    const list = document.getElementById("cart-items");
    const totalEl = document.getElementById("cart-total");
    if (!list || !totalEl) return;

    list.innerHTML = "";

    const entries = Array.from(state.cart.values());
    if (!entries.length) {
        const empty = document.createElement("li");
        empty.className = "empty";
        empty.textContent = "Your cart is empty.";
        list.appendChild(empty);
        totalEl.textContent = "0.00";
        return;
    }

    let total = 0;
    entries.forEach(({ product, quantity }) => {
        const lineTotal = Number(product.price) * quantity;
        total += lineTotal;

        const item = document.createElement("li");

        const details = document.createElement("div");
        details.className = "cart-item-details";
        details.innerHTML = `<strong>${product.name}</strong><span>${quantity} × $${Number(product.price).toFixed(2)} (${product.subcategory})</span>`;

        const actions = document.createElement("div");
        actions.className = "cart-item-actions";

        const qtyInput = document.createElement("input");
        qtyInput.type = "number";
        qtyInput.min = "1";
        qtyInput.value = quantity;
        qtyInput.addEventListener("change", (event) => {
            const nextValue = parseInt(event.target.value, 10);
            if (Number.isNaN(nextValue) || nextValue < 1) {
                event.target.value = quantity;
            } else {
                updateCartQuantity(product.id, nextValue);
            }
        });

        const removeButton = document.createElement("button");
        removeButton.type = "button";
        removeButton.textContent = "Remove";
        removeButton.addEventListener("click", () => removeFromCart(product.id));

        actions.appendChild(qtyInput);
        actions.appendChild(removeButton);

        const price = document.createElement("strong");
        price.textContent = `$${lineTotal.toFixed(2)}`;

        item.appendChild(details);
        item.appendChild(actions);
        item.appendChild(price);

        list.appendChild(item);
    });

    totalEl.textContent = total.toFixed(2);
}

function bindCheckoutForm() {
    const form = document.getElementById("checkout-form");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const messageBox = document.getElementById("form-messages");
        if (!messageBox) return;

        const items = Array.from(state.cart.values()).map(({ product, quantity }) => ({
            productId: product.id,
            quantity,
        }));

        if (!items.length) {
            showMessage(messageBox, "Please add at least one item to your cart.", "error");
            return;
        }

        const formData = new FormData(form);
        const payload = {
            customerName: formData.get("customerName")?.toString().trim(),
            email: formData.get("email")?.toString().trim(),
            phone: formData.get("phone")?.toString().trim(),
            address: formData.get("address")?.toString().trim(),
            items,
        };

        try {
            const response = await fetch("/api/orders", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ error: "Checkout failed." }));
                throw new Error(error.error || "Checkout failed.");
            }

            const result = await response.json();
            showMessage(
                messageBox,
                result.message || "Order received! We will confirm delivery details shortly.",
                "success"
            );
            state.cart.clear();
            renderCart();
            form.reset();
        } catch (error) {
            showMessage(messageBox, error.message || "Checkout failed.", "error");
        }
    });
}

function showMessage(target, message, type) {
    target.textContent = message;
    target.className = `form-messages ${type}`;
}
