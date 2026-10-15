describe('SC11: Write Review', () => {
  // เปิดหน้ารายละเอียดสินค้าตามลำดับ
  const openProductByIndex = (productIndex = 0) => {
    cy.visit('/products');

    cy.get('.features_items').should('be.visible');

    cy.get('a[href*="/product_details/"]:visible').then(($links) => {
      // แปลง jQuery collection เป็น Array และตัด URL ซ้ำออก
      const productUrls = [
        ...new Set(
          $links.toArray().map((link) => link.getAttribute('href'))
        ),
      ].filter(Boolean);

      expect(
        productUrls.length,
        'จำนวนลิงก์สินค้าที่พบ'
      ).to.be.greaterThan(productIndex);

      cy.visit(productUrls[productIndex]);
    });

    cy.url().should('include', '/product_details/');

    cy.get('#name').should('be.visible');
    cy.get('#email').should('be.visible');
    cy.get('#review').should('be.visible');
  };

  // กรอกข้อมูลและส่งรีวิว
  const fillAndSubmitReview = (name, email, review) => {
    cy.get('#name').clear().type(name);
    cy.get('#email').clear().type(email);
    cy.get('#review').clear().type(review);

    // ตรวจสอบข้อมูลก่อนส่ง
    cy.get('#name').should('have.value', name);
    cy.get('#email').should('have.value', email);
    cy.get('#review').should('have.value', review);

    cy.get('#button-review')
      .should('be.visible')
      .click();
  };

  // TC_SC11_01: ตรวจสอบว่ามีแบบฟอร์มรีวิว
  it('TC_SC11_01: Review form exists', () => {
    openProductByIndex(0);

    cy.contains(/Write Your Review/i).should('be.visible');

    cy.screenshot('TC_SC11_01_review_form_exists');
  });

  // TC_SC11_02: ตรวจสอบช่องกรอกข้อมูล
  it('TC_SC11_02: Review fields exist', () => {
    openProductByIndex(1);

    cy.get('#name').should('be.visible');
    cy.get('#email').should('be.visible');
    cy.get('#review').should('be.visible');

    fillAndSubmitReview(
      'Checker User',
      'checker@example.com',
      'Checking all review input fields.'
    );

    cy.screenshot('TC_SC11_02_review_fields');
  });

  // TC_SC11_03: ทดสอบกรอกชื่อและอีเมล
  it('TC_SC11_03: Review form accepts name and email', () => {
    openProductByIndex(2);

    const name = 'Somchai Jaidee';
    const email = 'somchai.j@example.com';

    fillAndSubmitReview(
      name,
      email,
      'Testing valid name and email entry.'
    );

    cy.screenshot('TC_SC11_03_entered_name_email');
  });

  // TC_SC11_04: ทดสอบกรอกข้อความรีวิว
  it('TC_SC11_04: Review text can be entered', () => {
    openProductByIndex(3);

    const review =
      'The product quality is superb! Highly satisfied with this order.';

    fillAndSubmitReview(
      'Reviewer Person',
      'reviewer@example.com',
      review
    );

    cy.screenshot('TC_SC11_04_entered_review_text');
  });

  // TC_SC11_05: ทดสอบอักขระพิเศษ
  it('TC_SC11_05: Review accepts special characters', () => {
    openProductByIndex(4);

    const review =
      'Rating: 5/5 stars! Code: #PRD-99 @Home (100% Recommended)!!!';

    fillAndSubmitReview(
      'Special Tester',
      'special.test@example.com',
      review
    );

    cy.screenshot('TC_SC11_05_entered_special_chars');
  });
});