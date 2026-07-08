import React, { useState, useEffect } from 'react';
import { Container, Table, Button, Modal, Form, Row, Col } from 'react-bootstrap';
import Header from "../components/header";
import NavBar from "../components/navbar";
import Footer from "../components/footer";
import ReactGA from "react-ga4";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5001/api/products";

const EMPTY_FORM = {
    'Product': '',
    'Primary Disease': '',
    'FRAC': '',
    'omri': 0,
    'phi': 0,
    'Max Applications': 999,
    'Container Size': 0,
    'units': '',
    'Price': 0,
    'Dose (avg)': 0,
    'Cost/Dose': 0,
    'package_size': 0,
    'price_source': '',
    'label_url': '',
    'rei': 0,
    'ppe_long_sleeves_pants': false,
    'ppe_socks_shoes': false,
    'ppe_waterproof_gloves': false,
    'ppe_protective_eyewear': false,
    'min_rate': 0,
    'max_rate': 0,
    'EPA No': '',
    'Active Ingredient': '',
    'Singal Word': '',
    'effectiveness': {
        "Anthracnose": "na",
        "Black Rot": "na",
        "Bitter Rot": "na",
        "Botrytis": "na",
        "Downy": "na",
        "Phomopsis": "na",
        "Powdery": "na"
    }
};

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
            setFormData({ ...EMPTY_FORM });
        }
        setShowModal(true);
    };

    const handleClose = () => setShowModal(false);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        if (name.includes('.')) {
            const [parent, child] = name.split('.');
            setFormData({
                ...formData,
                [parent]: {
                    ...formData[parent],
                    [child]: value
                }
            });
        } else if (type === 'checkbox') {
            setFormData({ ...formData, [name]: checked });
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
        <Container fluid className="px-0 w-100">
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
                            <th>Active Ingredient</th>
                            <th>Min Rate</th>
                            <th>Max Rate</th>
                            <th>Units</th>
                            <th>PHI</th>
                            <th>REI</th>
                            <th>Cost/Dose</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {products.map((p) => (
                            <tr key={p.Product}>
                                <td>{p.Product}</td>
                                <td>{p.FRAC}</td>
                                <td>{p['Active Ingredient'] || '-'}</td>
                                <td>{p.min_rate}</td>
                                <td>{p.max_rate}</td>   
                                <td>{p.units}</td>
                                <td>{p.phi}</td>
                                <td>{p.rei}</td>
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

                        {/* ── Basic Info ── */}
                        <h5 className="mb-2">Basic Information</h5>
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
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Active Ingredient</Form.Label>
                                    <Form.Control type="text" name="Active Ingredient" value={formData['Active Ingredient'] || ''} onChange={handleChange} maxLength={200} placeholder="e.g. Mancozeb" />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>EPA Reg No</Form.Label>
                                    <Form.Control type="text" name="EPA No" value={formData['EPA No'] || ''} onChange={handleChange} placeholder="e.g. 70506-234" />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Signal Word</Form.Label>
                                    <Form.Control type="text" name="Singal Word" value={formData['Singal Word'] || ''} onChange={handleChange} placeholder="caution, warning" />
                                </Form.Group>
                            </Col>
                        </Row>

                        <Row>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>FRAC</Form.Label>
                                    <Form.Control type="text" name="FRAC" value={formData.FRAC || ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>OMRI</Form.Label>
                                    <Form.Select name="omri" value={formData.omri ?? 0} onChange={handleChange}>
                                        <option value={0}>No</option>
                                        <option value={1}>Yes</option>
                                    </Form.Select>
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>PHI (days)</Form.Label>
                                    <Form.Control type="number" name="phi" value={formData.phi ?? 0} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>REI (hours)</Form.Label>
                                    <Form.Control type="number" name="rei" value={formData.rei ?? 0} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Max Applications</Form.Label>
                                    <Form.Control type="number" name="Max Applications" value={formData['Max Applications'] ?? 999} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Units</Form.Label>
                                    <Form.Control type="text" name="units" value={formData.units || ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Label URL</Form.Label>
                                    <Form.Control type="url" name="label_url" value={formData.label_url || ''} onChange={handleChange} placeholder="https://..." />
                                </Form.Group>
                            </Col>
                        </Row>

                        {/* ── Pricing & Packaging ── */}
                        <hr />
                        <h5 className="mb-2">Pricing &amp; Packaging</h5>
                        <Row>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Price ($)</Form.Label>
                                    <Form.Control type="number" step="0.01" name="Price" value={formData.Price ?? 0} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Price Source</Form.Label>
                                    <Form.Control type="text" name="price_source" value={formData.price_source || ''} onChange={handleChange} placeholder="e.g. Amazon, Local co-op" />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Container Size</Form.Label>
                                    <Form.Control type="number" step="0.01" name="Container Size" value={formData['Container Size'] ?? 0} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Package Size</Form.Label>
                                    <Form.Control type="number" step="0.1" name="package_size" value={formData.package_size ?? 0} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Dose (avg)</Form.Label>
                                    <Form.Control type="number" step="0.01" name="Dose (avg)" value={formData['Dose (avg)'] ?? 0} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Cost/Dose ($)</Form.Label>
                                    <Form.Control type="number" step="0.01" name="Cost/Dose" value={formData['Cost/Dose'] ?? 0} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                        </Row>

                        {/* ── Application Rates ── */}
                        <hr />
                        <h5 className="mb-2">Application Rates</h5>
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Minimum Rate</Form.Label>
                                    <Form.Control type="number" step="0.1" name="min_rate" value={formData.min_rate ?? 0} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Maximum Rate</Form.Label>
                                    <Form.Control type="number" step="0.1" name="max_rate" value={formData.max_rate ?? 0} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                        </Row>

                        {/* ── Applicator PPE ── */}
                        <hr />
                        <h5 className="mb-2">Applicator PPE Requirements</h5>
                        <Row>
                            <Col md={6}>
                                <Form.Check
                                    type="checkbox"
                                    id="ppe_long_sleeves_pants"
                                    name="ppe_long_sleeves_pants"
                                    label="Long Sleeves and Pants"
                                    checked={!!formData.ppe_long_sleeves_pants}
                                    onChange={handleChange}
                                    className="mb-2"
                                />
                            </Col>
                            <Col md={6}>
                                <Form.Check
                                    type="checkbox"
                                    id="ppe_socks_shoes"
                                    name="ppe_socks_shoes"
                                    label="Socks and Shoes"
                                    checked={!!formData.ppe_socks_shoes}
                                    onChange={handleChange}
                                    className="mb-2"
                                />
                            </Col>
                            <Col md={6}>
                                <Form.Check
                                    type="checkbox"
                                    id="ppe_waterproof_gloves"
                                    name="ppe_waterproof_gloves"
                                    label="Waterproof Gloves"
                                    checked={!!formData.ppe_waterproof_gloves}
                                    onChange={handleChange}
                                    className="mb-2"
                                />
                            </Col>
                            <Col md={6}>
                                <Form.Check
                                    type="checkbox"
                                    id="ppe_protective_eyewear"
                                    name="ppe_protective_eyewear"
                                    label="Protective Eyewear"
                                    checked={!!formData.ppe_protective_eyewear}
                                    onChange={handleChange}
                                    className="mb-2"
                                />
                            </Col>
                        </Row>

                        {/* ── Disease Effectiveness ── */}
                        <hr />
                        <h5 className="mb-2">Disease Effectiveness</h5>
                        <Row>
                            {formData.effectiveness && Object.keys(formData.effectiveness).map((disease) => (
                                <Col md={4} key={disease}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>{disease}</Form.Label>
                                        <Form.Select name={`effectiveness.${disease}`} value={formData.effectiveness[disease]} onChange={handleChange}>
                                            <option value="na">na</option>
                                            <option value="f">f (Fair)</option>
                                            <option value="g">g (Good)</option>
                                            <option value="vg">vg (Very Good)</option>
                                            <option value="e">e (Excellent)</option>
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
