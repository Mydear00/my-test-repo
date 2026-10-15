describe('SC10: Checking Out', () => {
  // เปิดหน้ารถเข็น
  const openCart = () => {
    cy.visit('/view_cart');
  };

  // เพิ่มสินค้าตามลำดับที่กำหนด
  const addProductToCart = (productIndex = 0) => {
    cy.visit('/products');

    cy.get('.features_items').should('be.visible');

    cy.get('.productinfo a.add-to-cart')
      .should('have.length.greaterThan', productIndex)
      .eq(productIndex)
      .click({ force: true });

    cy.get('.modal-content').should('be.visible');

    cy.get('.modal-content .close-modal')
      .should('be.visible')
      .click({ force: true });

    cy.get('.modal-content').should('not.be.visible');
  };

  // TC_SC10_01: ตรวจสอบว่าหน้ารถเข็นเปิดได้
  it('TC_SC10_01: Cart page opens', () => {
    openCart();

    cy.url().should('include', '/view_cart');
    cy.get('body').should('be.visible');

    cy.screenshot('TC_SC10_01_cart_page');
  });

  // TC_SC10_02: ตรวจสอบรถเข็นว่าง
  it('TC_SC10_02: Empty cart message', () => {
    openCart();

    cy.get('body').should('be.visible');

    cy.get('body').then(($body) => {
      const productRows = $body.find(
        '#cart_info_table tbody tr[id^="product-"]'
      );

      const bodyText = $body.text().toLowerCase();

      const emptyMessage =
        bodyText.includes('cart is empty') ||
        bodyText.includes('empty cart');

      expect(
        productRows.length === 0 || emptyMessage,
        'รถเข็นต้องไม่มีสินค้า หรือแสดงข้อความว่ารถเข็นว่าง'
      ).to.equal(true);
    });

    cy.screenshot('TC_SC10_02_empty_cart');
  });

  // TC_SC10_03: เพิ่มสินค้าและตรวจสอบในรถเข็น
  it('TC_SC10_03: Add product to cart', () => {
    addProductToCart(0);
    openCart();

    cy.get('#cart_info_table tbody tr[id^="product-"]')
      .should('have.length.greaterThan', 0);

    cy.screenshot('TC_SC10_03_added_product_in_cart');
  });

  // TC_SC10_04: Guest Checkout ต้องเข้าสู่ระบบก่อน
  it('TC_SC10_04: Guest checkout requires login', () => {
    addProductToCart(0);
    openCart();

    cy.get('.btn.btn-default.check_out')
      .should('be.visible')
      .click();

    cy.get('body').should('be.visible');

    cy.contains(/Register\s*\/\s*Login/i).should('be.visible');

    cy.screenshot('TC_SC10_04_checkout_redirect_login');
  });

  // TC_SC10_05: เพิ่มสินค้าสองรายการ
  it('TC_SC10_05: Multiple products in cart', () => {
    addProductToCart(0);
    addProductToCart(1);
    openCart();

    cy.get('#cart_info_table tbody tr[id^="product-"]')
      .should('have.length.greaterThan', 1);

    cy.screenshot('TC_SC10_05_multiple_products_in_cart');
  });
});