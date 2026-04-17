import React, { useState, useEffect } from 'react';
import { Container, Table, Button, Modal, Form, Row, Col } from 'react-bootstrap';
import Header from "../components/header";
import NavBar from "../components/navbar";
import Footer from "../home/footer";
import ReactGA from "react-ga4";

const API_BASE = "http://localhost:5001/api/products";

const ProductManagement = () => {
    ReactGA.send({ hitType: "pageview", page: "/database", title: "Product Management" });

    const [products, setProducts] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [originalName, setOriginalName] = useState(null);
    const [formData, setFormData] = useState({});

    useEffect(() => {
        fetchProducts();
    }, []);

    const fetchProducts = async () => {
        try {
            const response = await fetch(API_BASE);
            const data = await response.json();
            setProducts(data);
        } catch (error) {
            console.error("Error fetching products:", error);
        }
    };

    const handleShow = (product = null) => {
        if (product) {
            setOriginalName(product.Product);
            setFormData({ ...product });
        } else {
            setOriginalName(null);
            setFormData({
                'Product': '',
                'Primary Disease': '',
                'FRAC': '',
                'omri': '',
                'phi': 0,
                'Max Applications': 999,
                'Container Size': 0,
                'units': '',
                'Price': 0,
                'Dose (avg)': 0,
                'Cost/Dose': 0,
                'effectiveness': {
                    "Anthracnose": "na",
                    "Black Rot": "na",
                    "Bitter Rot": "na",
                    "Botrytis": "na",
                    "Downy": "na",
                    "Phomopsis": "na",
                    "Powdery": "na"
                }
            });
        }
        setShowModal(true);
    };

    const handleClose = () => setShowModal(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        if (name.includes('.')) {
            const [parent, child] = name.split('.');
            setFormData({
                ...formData,
                [parent]: {
                    ...formData[parent],
                    [child]: value
                }
            });
        } else {
            setFormData({ ...formData, [name]: value });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const method = originalName ? "PUT" : "POST";
        const url = originalName ? `${API_BASE}/${originalName}` : API_BASE;

        console.log("Submitting:", { method, url, formData });

        try {
            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            if (response.ok) {
                alert("Product saved successfully!");
                fetchProducts();
                handleClose();
            } else {
                const errorData = await response.text();
                alert("Error saving product: " + response.status + " " + errorData);
            }
        } catch (error) {
            console.error("Error saving product:", error);
            alert("Network error: " + error.message);
        }
    };

    const handleDelete = async (name) => {
        if (window.confirm(`Are you sure you want to delete ${name}?`)) {
            try {
                const response = await fetch(`${API_BASE}/${name}`, {
                    method: 'DELETE'
                });
                if (response.ok) {
                    fetchProducts();
                }
            } catch (error) {
                console.error("Error deleting product:", error);
            }
        }
    };

    return (
        <Container>
            <Row><Header /></Row>
            <Row className="navbar"><NavBar /></Row>
            
            <div className="mt-4">
                <h2>Spray Chemical Database</h2>
                <Button variant="primary" className="mb-3" onClick={() => handleShow()}>Add New Product</Button>
                
                <Table striped bordered hover responsive>
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>FRAC</th>
                            <th>OMRI</th>
                            <th>PHI</th>
                            <th>Cost/Dose</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map((p) => (
                            <tr key={p.Product}>
                                <td>{p.Product}</td>
                                <td>{p.FRAC}</td>
                                <td>{p.omri}</td>
                                <td>{p.phi}</td>
                                <td>${p['Cost/Dose']?.toFixed(2)}</td>
                                <td>
                                    <Button variant="info" size="sm" className="me-2" onClick={() => handleShow(p)}>Edit</Button>
                                    <Button variant="danger" size="sm" onClick={() => handleDelete(p.Product)}>Delete</Button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </div>

            <Modal show={showModal} onHide={handleClose} size="lg">
                <Modal.Header closeButton>
                    <Modal.Title>{originalName ? "Edit Product" : "Add Product"}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form onSubmit={handleSubmit}>
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Product Name</Form.Label>
                                    <Form.Control type="text" name="Product" value={formData.Product || ''} onChange={handleChange} required />
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Primary Disease</Form.Label>
                                    <Form.Control type="text" name="Primary Disease" value={formData['Primary Disease'] || ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>FRAC</Form.Label>
                                    <Form.Control type="text" name="FRAC" value={formData.FRAC || ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>OMRI</Form.Label>
                                    <Form.Select name="omri" value={formData.omri} onChange={handleChange}>
                                        <option value={0}>No</option>
                                        <option value={1}>Yes</option>
                                    </Form.Select>
                                    </Form.Group>
                                    </Col>
                                    <Col md={4}>
                                    <Form.Group className="mb-3">
                                    <Form.Label>PHI</Form.Label>
                                    <Form.Control type="number" name="phi" value={formData.phi || 0} onChange={handleChange} />
                                    </Form.Group>
                                    </Col>
                                    </Row>
                                    <Row>
                                    <Col md={4}>
                                    <Form.Group className="mb-3">
                                    <Form.Label>Price ($)</Form.Label>
                                    <Form.Control type="number" step="0.01" name="Price" value={formData.Price || 0} onChange={handleChange} />
                                    </Form.Group>
                                    </Col>
                                    <Col md={4}>
                                    <Form.Group className="mb-3">
                                    <Form.Label>Dose (avg)</Form.Label>
                                    <Form.Control type="number" step="0.01" name="Dose (avg)" value={formData['Dose (avg)'] || 0} onChange={handleChange} />
                                    </Form.Group>
                                    </Col>
                                    <Col md={4}>
                                    <Form.Group className="mb-3">
                                    <Form.Label>Cost/Dose ($)</Form.Label>
                                    <Form.Control type="number" step="0.01" name="Cost/Dose" value={formData['Cost/Dose'] || 0} onChange={handleChange} />
                                    </Form.Group>
                                    </Col>
                                    </Row>

                                    <h5>Effectiveness</h5>
                                    <Row>
                                    {formData.effectiveness && Object.keys(formData.effectiveness).map((disease) => (
                                    <Col md={4} key={disease}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>{disease}</Form.Label>
                                        <Form.Select name={`effectiveness.${disease}`} value={formData.effectiveness[disease]} onChange={handleChange}>
                                            <option value="na">na</option>
                                            <option value="poor">poor</option>
                                            <option value="fair">fair</option>
                                            <option value="good">good</option>
                                            <option value="excellent">excellent</option>
                                        </Form.Select>
                                    </Form.Group>
                                    </Col>
                                    ))}
                                    </Row>
                        <Button variant="primary" type="submit">Save Changes</Button>
                    </Form>
                </Modal.Body>
            </Modal>

            <Row><Footer /></Row>
        </Container>
    );
};

export default ProductManagement;
