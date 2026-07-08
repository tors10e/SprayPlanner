import React, { useState, useEffect } from 'react';
import { Container, Table, Button, Modal, Form, Row, Col, Card, Alert } from 'react-bootstrap';
import Header from "../components/header";
import NavBar from "../components/navbar";
import Footer from "../components/footer";
import ReactGA from "react-ga4";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5001/api/products";
const HISTORY_API = API_BASE.replace('/products', '/history');

const EMPTY_HISTORY_FORM = {
    "Spray #": "",
    "Date": "",
    "End Time": "",
    "Block ": "",
    "Pesticide": "",
    "EPA No": "",
    "Group": "",
    "Active Ingredient": "",
    "Pest": "",
    "Singal Word": "",
    "REI (h)": "",
    "PHI (d)": "",
    "Units": "",
    "PHI Date": "",
    "REI_TIME": "",
    "Liters/Acre": "",
    "Min Dose": "",
    "Max Dose": "",
    "Dose/acre": "",
    "Dose per L @150 l": "",
    "Rate Units": "",
    "Calculated Dose": "",
    "Dose Units": "",
    "Actual Amt/acre": "",
    "Notes": ""
};

const SprayHistory = () => {
    ReactGA.send({ hitType: "pageview", page: "/history", title: "Spray History" });

    const [history, setHistory] = useState([]);
    const [products, setProducts] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [currentId, setCurrentId] = useState(null);
    const [formData, setFormData] = useState({});
    
    // File upload state
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState({ type: '', message: '' });

    useEffect(() => {
        fetchHistory();
        fetchProducts();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await fetch(HISTORY_API);
            const data = await response.json();
            setHistory(data);
        } catch (error) {
            console.error("Error fetching history:", error);
        }
    };

    const fetchProducts = async () => {
        try {
            const response = await fetch(API_BASE);
            const data = await response.json();
            setProducts(data);
        } catch (error) {
            console.error("Error fetching products:", error);
        }
    };

    const handleShow = (entry = null) => {
        if (entry) {
            setCurrentId(entry.id);
            setFormData({ ...entry });
        } else {
            setCurrentId(null);
            setFormData({ ...EMPTY_HISTORY_FORM });
        }
        setShowModal(true);
    };

    const handleClose = () => setShowModal(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleProductSelect = (e) => {
        const productName = e.target.value;
        const product = products.find(p => p.Product === productName);
        if (product) {
            setFormData({
                ...formData,
                "Pesticide": productName,
                "Group": product.FRAC || '',
                "EPA No": product["EPA No"] || '',
                "Active Ingredient": product["Active Ingredient"] || '',
                "Singal Word": product["Singal Word"] || '',
                "REI (h)": product.rei || 0,
                "PHI (d)": product.phi || 0,
                "Units": product.units || '',
                "Min Dose": product.min_rate || 0,
                "Max Dose": product.max_rate || 0,
                "Rate Units": product.units || ''
            });
        } else {
            setFormData({
                ...formData,
                "Pesticide": productName
            });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const method = currentId ? "PUT" : "POST";
        const url = currentId ? `${HISTORY_API}/${currentId}` : HISTORY_API;

        // Clean numeric types for sending to database
        const payload = {};
        Object.keys(formData).forEach(key => {
            let val = formData[key];
            if (["Spray #", "REI (h)", "PHI (d)", "Liters/Acre", "Min Dose", "Max Dose", "Dose/acre", "Dose per L @150 l", "Calculated Dose", "Actual Amt/acre"].includes(key)) {
                val = val === "" || val === null || val === undefined ? null : Number(val);
            }
            payload[key] = val;
        });

        try {
            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                alert("History entry saved successfully!");
                fetchHistory();
                handleClose();
            } else {
                const errorData = await response.text();
                alert("Error saving history: " + response.status + " " + errorData);
            }
        } catch (error) {
            console.error("Error saving history:", error);
            alert("Network error: " + error.message);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm("Are you sure you want to delete this history log entry?")) {
            try {
                const response = await fetch(`${HISTORY_API}/${id}`, {
                    method: 'DELETE'
                });
                if (response.ok) {
                    fetchHistory();
                }
            } catch (error) {
                console.error("Error deleting history entry:", error);
            }
        }
    };

    // CSV upload handlers
    const handleFileChange = (e) => {
        setSelectedFile(e.target.files[0]);
        setUploadStatus({ type: '', message: '' });
    };

    const handleFileUpload = async (e) => {
        e.preventDefault();
        if (!selectedFile) {
            setUploadStatus({ type: 'danger', message: 'Please select a CSV file first.' });
            return;
        }

        const uploadData = new FormData();
        uploadData.append('file', selectedFile);

        try {
            const response = await fetch(`${HISTORY_API}/upload`, {
                method: 'POST',
                body: uploadData
            });
            const result = await response.json();
            if (response.ok) {
                setUploadStatus({ 
                    type: 'success', 
                    message: `Bulk upload successful! Imported ${result.inserted} records.` 
                });
                fetchHistory();
                setSelectedFile(null);
                // Reset file input value
                document.getElementById('csvFileInput').value = '';
            } else {
                setUploadStatus({ 
                    type: 'danger', 
                    message: `Upload failed: ${result.message || 'Unknown error'}` 
                });
            }
        } catch (error) {
            console.error("Upload error:", error);
            setUploadStatus({ type: 'danger', message: `Network error: ${error.message}` });
        }
    };

    // Stats calculations
    const totalApplications = history.length;
    const treatedBlocks = new Set(history.map(h => h["Block "]).filter(Boolean)).size;
    const uniqueChemicals = new Set(history.map(h => h["Pesticide"]).filter(Boolean)).size;

    return (
        <Container>
            <Row><Header /></Row>
            <Row className="navbar"><NavBar /></Row>

            <div className="mt-4">
                <h2>Pesticide Application History</h2>
                
                {/* ── Summary KPIs ── */}
                <Row className="mb-4 mt-3">
                    <Col md={4}>
                        <Card className="text-center border-0 shadow-sm bg-light">
                            <Card.Body>
                                <Card.Title className="text-secondary small uppercase">Total Logs</Card.Title>
                                <Card.Text className="h2 font-weight-bold text-primary">{totalApplications}</Card.Text>
                            </Card.Body>
                        </Card>
                    </Col>
                    <Col md={4}>
                        <Card className="text-center border-0 shadow-sm bg-light">
                            <Card.Body>
                                <Card.Title className="text-secondary small uppercase">Blocks Treated</Card.Title>
                                <Card.Text className="h2 font-weight-bold text-success">{treatedBlocks}</Card.Text>
                            </Card.Body>
                        </Card>
                    </Col>
                    <Col md={4}>
                        <Card className="text-center border-0 shadow-sm bg-light">
                            <Card.Body>
                                <Card.Title className="text-secondary small uppercase">Unique Chemicals</Card.Title>
                                <Card.Text className="h2 font-weight-bold text-warning">{uniqueChemicals}</Card.Text>
                            </Card.Body>
                        </Card>
                    </Col>
                </Row>

                {/* ── Actions (Add & Upload CSV) ── */}
                <Row className="mb-3 align-items-center">
                    <Col md={6}>
                        <Button variant="primary" onClick={() => handleShow()}>Add New Log</Button>
                    </Col>
                    <Col md={6} className="text-md-end mt-2 mt-md-0">
                        <Form onSubmit={handleFileUpload} className="d-inline-flex align-items-center">
                            <Form.Control 
                                type="file" 
                                accept=".csv" 
                                onChange={handleFileChange}
                                size="sm"
                                id="csvFileInput"
                                className="me-2"
                                style={{ maxWidth: '250px' }}
                            />
                            <Button type="submit" variant="outline-success" size="sm">Import CSV</Button>
                        </Form>
                    </Col>
                </Row>

                {uploadStatus.message && (
                    <Alert variant={uploadStatus.type} dismissible onClose={() => setUploadStatus({ type: '', message: '' })}>
                        {uploadStatus.message}
                    </Alert>
                )}

                {/* ── Spray Log Table ── */}
                <Table striped bordered hover responsive className="shadow-sm bg-white rounded">
                    <thead className="table-dark">
                        <tr>
                            <th>Date</th>
                            <th>Spray #</th>
                            <th>Block</th>
                            <th>Pesticide</th>
                            <th>EPA No</th>
                            <th>Dose/acre</th>
                            <th>Liters/Acre</th>
                            <th>Notes</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {history.map((h) => (
                            <tr key={h.id}>
                                <td>{h["Date"] || '-'}</td>
                                <td>{h["Spray #"] || '-'}</td>
                                <td>{h["Block "] || '-'}</td>
                                <td>{h["Pesticide"] || '-'}</td>
                                <td>{h["EPA No"] || '-'}</td>
                                <td>{h["Dose/acre"] ? `${h["Dose/acre"]} ${h["Rate Units"] || ''}` : '-'}</td>
                                <td>{h["Liters/Acre"] || '-'}</td>
                                <td><small className="text-muted">{h["Notes"]}</small></td>
                                <td>
                                    <Button variant="info" size="sm" className="me-2" onClick={() => handleShow(h)}>Edit</Button>
                                    <Button variant="danger" size="sm" onClick={() => handleDelete(h.id)}>Delete</Button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </div>

            {/* ── CRUD Modal ── */}
            <Modal show={showModal} onHide={handleClose} size="lg">
                <Modal.Header closeButton>
                    <Modal.Title>{currentId ? "Edit Log Entry" : "Add Log Entry"}</Modal.Title>
                </Modal.Header>
                <Modal.Body style={{ maxHeight: 'calc(100vh - 210px)', overflowY: 'auto' }}>
                    <Form onSubmit={handleSubmit}>
                        
                        {/* ── Block 1: Basic Details ── */}
                        <h5>Basic Log Details</h5>
                        <Row>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Spray #</Form.Label>
                                    <Form.Control type="number" name="Spray #" value={formData["Spray #"] ?? ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Date</Form.Label>
                                    <Form.Control type="text" placeholder="MM/DD/YY" name="Date" value={formData["Date"] || ''} onChange={handleChange} required />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>End Time</Form.Label>
                                    <Form.Control type="text" placeholder="HHMM or NA" name="End Time" value={formData["End Time"] || ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Block</Form.Label>
                                    <Form.Control type="text" placeholder="e.g. cs, pm, tr" name="Block " value={formData["Block "] || ''} onChange={handleChange} required />
                                </Form.Group>
                            </Col>
                        </Row>

                        {/* ── Block 2: Chemical Information ── */}
                        <hr />
                        <h5>Chemical Details</h5>
                        <Row>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Pesticide Product</Form.Label>
                                    <Form.Select name="Pesticide" value={formData["Pesticide"] || ''} onChange={handleProductSelect} required>
                                        <option value="">-- Select Product --</option>
                                        {products.map(p => (
                                            <option key={p.Product} value={p.Product}>{p.Product}</option>
                                        ))}
                                    </Form.Select>
                                </Form.Group>
                            </Col>
                             <Col md={4}>
                                 <Form.Group className="mb-3">
                                     <Form.Label>EPA Reg No</Form.Label>
                                     <Form.Control type="text" name="EPA No" value={formData["EPA No"] || ''} readOnly />
                                 </Form.Group>
                             </Col>
                             <Col md={4}>
                                 <Form.Group className="mb-3">
                                     <Form.Label>Chemical Group</Form.Label>
                                     <Form.Control type="text" name="Group" value={formData["Group"] || ''} readOnly />
                                 </Form.Group>
                             </Col>

                        </Row>
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Active Ingredient</Form.Label>
                                    <Form.Control type="text" name="Active Ingredient" value={formData["Active Ingredient"] || ''} readOnly />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Target Pest</Form.Label>
                                    <Form.Control type="text" name="Pest" value={formData["Pest"] || ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Signal Word</Form.Label>
                                    <Form.Control type="text" placeholder="caution, warning" name="Singal Word" value={formData["Singal Word"] || ''} readOnly />
                                </Form.Group>
                            </Col>

                        </Row>

                        {/* ── Block 3: Safety & Restrictions ── */}
                        <hr />
                        <h5>Safety &amp; Compliance</h5>
                        <Row>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>REI (hours)</Form.Label>
                                    <Form.Control type="number" name="REI (h)" value={formData["REI (h)"] ?? ''} readOnly />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>PHI (days)</Form.Label>
                                    <Form.Control type="number" name="PHI (d)" value={formData["PHI (d)"] ?? ''} readOnly />
                                </Form.Group>
                            </Col>

                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>REI Clear Time</Form.Label>
                                    <Form.Control type="text" placeholder="e.g. 1700" name="REI_TIME" value={formData["REI_TIME"] || ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>PHI Clear Date</Form.Label>
                                    <Form.Control type="text" placeholder="MM/DD/YY" name="PHI Date" value={formData["PHI Date"] || ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                        </Row>

                        {/* ── Block 4: Application Rates ── */}
                        <hr />
                        <h5>Rates &amp; Dilutions</h5>
                        <Row>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Water (Liters/Acre)</Form.Label>
                                    <Form.Control type="number" name="Liters/Acre" value={formData["Liters/Acre"] ?? ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Min Dose</Form.Label>
                                    <Form.Control type="number" step="0.001" name="Min Dose" value={formData["Min Dose"] ?? ''} readOnly />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Max Dose</Form.Label>
                                    <Form.Control type="number" step="0.001" name="Max Dose" value={formData["Max Dose"] ?? ''} readOnly />
                                </Form.Group>
                            </Col>

                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Dose/Acre</Form.Label>
                                    <Form.Control type="number" step="0.001" name="Dose/acre" value={formData["Dose/acre"] ?? ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Dose per Litre</Form.Label>
                                    <Form.Control type="number" step="0.0001" name="Dose per L @150 l" value={formData["Dose per L @150 l"] ?? ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Rate Units</Form.Label>
                                    <Form.Control type="text" placeholder="lbs, fl oz" name="Rate Units" value={formData["Rate Units"] || ''} readOnly />
                                </Form.Group>
                            </Col>

                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Calculated Dose</Form.Label>
                                    <Form.Control type="number" step="0.1" name="Calculated Dose" value={formData["Calculated Dose"] ?? ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Dose Units</Form.Label>
                                    <Form.Control type="text" placeholder="ml, g" name="Dose Units" value={formData["Dose Units"] || ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Actual Amount/Acre</Form.Label>
                                    <Form.Control type="number" step="0.01" name="Actual Amt/acre" value={formData["Actual Amt/acre"] ?? ''} onChange={handleChange} />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Product Units</Form.Label>
                                    <Form.Control type="text" placeholder="lbs, fl oz" name="Units" value={formData["Units"] || ''} readOnly />
                                </Form.Group>
                            </Col>

                        </Row>

                        <hr />
                        <Form.Group className="mb-3">
                            <Form.Label>Notes</Form.Label>
                            <Form.Control as="textarea" rows={3} name="Notes" value={formData["Notes"] || ''} onChange={handleChange} />
                        </Form.Group>

                        <Button variant="primary" type="submit">Save Changes</Button>
                    </Form>
                </Modal.Body>
            </Modal>

            <Row><Footer /></Row>
        </Container>
    );
};

export default SprayHistory;
