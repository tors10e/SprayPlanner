import React, { useState } from 'react';
import { Button, Form, Container, Row, Col } from 'react-bootstrap';

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });

  const [status, setStatus] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('Sending...');

    // Here, you would integrate the email sending logic.
    try {
      // Simulate an email send with a timeout
      await sendEmail(formData);
      setStatus('Email Sent!');
      setFormData({ name: '', email: '', message: '' });
    } catch (error) {
      setStatus('Error sending email. Please try again later.');
    }
  };

  // Mock function to simulate email sending
  const sendEmail = (data) => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (data.name && data.email && data.message) {
          resolve();
        } else {
          reject(new Error('Missing data'));
        }
      }, 2000);
    });
  };

  return (
    <Container className="mt-5">
      <Row>
        <Col md={{ span: 6, offset: 3 }}>
          <h2>Contact Us</h2>
          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="formName">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter your name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </Form.Group>

            <Form.Group controlId="formEmail">
              <Form.Label>Email address</Form.Label>
              <Form.Control
                type="email"
                placeholder="Enter your email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
              />
            </Form.Group>

            <Form.Group controlId="formMessage">
              <Form.Label>Message</Form.Label>
              <Form.Control
                as="textarea"
                rows={4}
                placeholder="Your message"
                name="message"
                value={formData.message}
                onChange={handleInputChange}
                required
              />
            </Form.Group>

            <Button variant="primary" type="submit">
              Submit
            </Button>
          </Form>

          {status && <p className="mt-3">{status}</p>}
        </Col>
      </Row>
    </Container>
  );
};

export default ContactForm;
