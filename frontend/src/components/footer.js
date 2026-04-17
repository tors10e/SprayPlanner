import React from 'react';
import { Container, Col, Row } from 'react-bootstrap';

export function Footer(props) {
    return (
        <Row id="footer" className="mt-5 py-4 border-top">
            <Col md={6}>
                    <h5 className="footer-heading">LOCATION:</h5>
                    <p>1821 Vandiver Mountain Road, Clarkesville, GA 30523</p>
                    <p>Latitude: 34&deg; 43' 46.8588" | Longitude: -83&deg; 29' 51.6228"</p>
            </Col>
            <Col md={6}>
                <h5 className="footer-heading">CONTACT:</h5>
                <p>info@terraincognitavineyard.com</p>
                <p>(828) 482-7382</p>
            </Col>
        </Row>
    );
}

export default Footer;
