import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Modal, Form, Badge, InputGroup } from 'react-bootstrap';
import ReactGA from 'react-ga4';

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:5001/api/blocks' : '/api/blocks';

const EMPTY_BLOCK = {
    block_code: '',
    varieties: '',
    acres: 1.0,
    vine_spacing: 6.0,
    row_spacing: 9.0,
    trellis_type: 'VSP',
    rootstock: '3309C',
    rows: []
};

const VineyardBlocks = () => {
    ReactGA.send({ hitType: "pageview", page: "/vineyard-blocks", title: "Vineyard Blocks" });

    const [blocks, setBlocks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [isEdit, setIsEdit] = useState(false);
    const [formData, setFormData] = useState({ ...EMPTY_BLOCK });
    const [expandedBlocks, setExpandedBlocks] = useState({});
    
    // Quick row generator states
    const [genNumRows, setGenNumRows] = useState(10);
    const [genRowLength, setGenRowLength] = useState(300);

    const [errorMsg, setErrorMsg] = useState('');

    useEffect(() => {
        fetchBlocks();
    }, []);

    const fetchBlocks = async () => {
        setLoading(true);
        try {
            const response = await fetch(API_BASE);
            if (response.ok) {
                const data = await response.json();
                setBlocks(data);
            }
        } catch (error) {
            console.error("Error fetching vineyard blocks:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleShow = (block = null) => {
        setErrorMsg('');
        if (block) {
            setIsEdit(true);
            setFormData({ ...block, rows: [...block.rows] });
        } else {
            setIsEdit(false);
            setFormData({ ...EMPTY_BLOCK, rows: [] });
        }
        setGenNumRows(10);
        setGenRowLength(300);
        setShowModal(true);
    };

    const handleClose = () => setShowModal(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        const val = (name === 'acres' || name === 'vine_spacing' || name === 'row_spacing') ? parseFloat(value) || 0 : value;
        setFormData(prev => ({
            ...prev,
            [name]: val
        }));
    };

    const handleRowChange = (index, field, value) => {
        const updatedRows = [...formData.rows];
        updatedRows[index][field] = field === 'row_number' ? parseInt(value) || 0 : parseFloat(value) || 0;
        setFormData(prev => ({
            ...prev,
            rows: updatedRows
        }));
    };

    const addRow = () => {
        const nextNum = formData.rows.length > 0 ? Math.max(...formData.rows.map(r => r.row_number)) + 1 : 1;
        setFormData(prev => ({
            ...prev,
            rows: [...prev.rows, { row_number: nextNum, row_length: 300 }]
        }));
    };

    const removeRow = (index) => {
        const updatedRows = formData.rows.filter((_, i) => i !== index);
        setFormData(prev => ({
            ...prev,
            rows: updatedRows
        }));
    };

    const generateRowsBulk = () => {
        const newRows = [];
        for (let i = 1; i <= genNumRows; i++) {
            newRows.push({
                row_number: i,
                row_length: genRowLength
            });
        }
        setFormData(prev => ({
            ...prev,
            rows: newRows
        }));
    };

    const toggleBlockExpand = (code) => {
        setExpandedBlocks(prev => ({
            ...prev,
            [code]: !prev[code]
        }));
    };

    const getBlockSummaryStats = (block) => {
        const totalRows = block.rows.length;
        const vineSpacing = block.vine_spacing || 1;
        const totalVines = block.rows.reduce((sum, r) => sum + Math.floor(r.row_length / vineSpacing), 0);
        return { totalRows, totalVines };
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMsg('');

        if (!formData.block_code.trim()) {
            setErrorMsg('Block code is required');
            return;
        }

        // Validate unique row numbers
        const rowNums = formData.rows.map(r => r.row_number);
        const uniqueRowNums = new Set(rowNums);
        if (rowNums.length !== uniqueRowNums.size) {
            setErrorMsg('Duplicate row numbers are not allowed');
            return;
        }

        const url = isEdit ? `${API_BASE}/${formData.block_code}` : API_BASE;
        const method = isEdit ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            if (response.ok) {
                setShowModal(false);
                fetchBlocks();
            } else {
                setErrorMsg(result.message || 'An error occurred while saving the block');
            }
        } catch (error) {
            console.error("Error saving vineyard block:", error);
            setErrorMsg('Network error saving block');
        }
    };

    const handleDelete = async (blockCode) => {
        if (!window.confirm(`Are you sure you want to delete Block ${blockCode}? This will also delete all of its rows.`)) {
            return;
        }
        try {
            const response = await fetch(`${API_BASE}/${blockCode}`, {
                method: 'DELETE'
            });
            if (response.ok) {
                fetchBlocks();
            }
        } catch (error) {
            console.error("Error deleting block:", error);
        }
    };

    return (
        <Container fluid className="py-4 px-md-5">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h1 className="h2 m-0 text-dark">Vineyard Blocks</h1>
                    <p className="text-secondary m-0">Configure your blocks, row configurations, and manage overall vine density.</p>
                </div>
                <Button variant="success" size="lg" className="shadow-sm" onClick={() => handleShow()}>
                    + Add Vineyard Block
                </Button>
            </div>

            <Card className="border-0 shadow-sm w-100 mb-4">
                <Card.Header className="bg-dark text-white py-3">
                    <h5 className="m-0">Block Configurations &amp; Density Details</h5>
                </Card.Header>
                <Card.Body className="p-0">
                    {loading ? (
                        <div className="p-5 text-center text-secondary">Loading blocks...</div>
                    ) : blocks.length === 0 ? (
                        <p className="text-muted italic p-4 text-center">No vineyard blocks configured yet.</p>
                    ) : (
                        <Table hover responsive className="m-0 bg-white">
                            <thead className="table-light">
                                <tr>
                                    <th style={{ width: '15%' }}>Block Code</th>
                                    <th>Varieties / Grapes</th>
                                    <th className="text-center">Acres</th>
                                    <th className="text-center">Spacing (Vine x Row)</th>
                                    <th>Trellis Type</th>
                                    <th>Rootstock</th>
                                    <th className="text-center">Total Density</th>
                                    <th className="text-center" style={{ width: '15%' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {blocks.map((block) => {
                                    const isExpanded = !!expandedBlocks[block.block_code];
                                    const stats = getBlockSummaryStats(block);
                                    return (
                                        <React.Fragment key={`block-row-${block.block_code}`}>
                                            <tr onClick={() => toggleBlockExpand(block.block_code)} style={{ cursor: 'pointer' }}>
                                                <td>
                                                    <span className="text-secondary me-2">
                                                        {isExpanded ? '▼' : '▶'}
                                                    </span>
                                                    <strong className="text-info">{block.block_code.toUpperCase()}</strong>
                                                </td>
                                                <td>{block.varieties || '-'}</td>
                                                <td className="text-center">{block.acres ? `${block.acres.toFixed(2)} ac` : '-'}</td>
                                                <td className="text-center text-muted">
                                                    {block.vine_spacing} ft × {block.row_spacing} ft
                                                </td>
                                                <td>
                                                    <Badge bg="secondary" style={{ fontSize: '12px' }}>
                                                        {block.trellis_type || 'N/A'}
                                                    </Badge>
                                                </td>
                                                <td>
                                                    <Badge bg="info" style={{ fontSize: '12px' }}>
                                                        {block.rootstock || 'N/A'}
                                                    </Badge>
                                                </td>
                                                <td className="text-center">
                                                    <Badge bg="success" className="me-1">
                                                        {stats.totalRows} Rows
                                                    </Badge>
                                                    <Badge bg="primary">
                                                        {stats.totalVines} Vines
                                                    </Badge>
                                                </td>
                                                <td className="text-center" onClick={(e) => e.stopPropagation()}>
                                                    <Button variant="outline-primary" size="sm" className="me-2" onClick={() => handleShow(block)}>
                                                        Edit
                                                    </Button>
                                                    <Button variant="outline-danger" size="sm" onClick={() => handleDelete(block.block_code)}>
                                                        Delete
                                                    </Button>
                                                </td>
                                            </tr>
                                            {isExpanded && (
                                                <tr>
                                                    <td colSpan={8} className="bg-light p-3">
                                                        <div className="border rounded bg-white p-3 shadow-sm">
                                                            <div className="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom">
                                                                <h6 className="m-0 text-secondary">
                                                                    Row Configurations for Block <strong>{block.block_code.toUpperCase()}</strong>
                                                                </h6>
                                                                <Badge bg="success" text="white">
                                                                    Vines calculated dynamically: Length / Spacing ({block.vine_spacing} ft)
                                                                </Badge>
                                                            </div>
                                                            {block.rows.length === 0 ? (
                                                                <p className="text-muted small m-0 italic">No row lengths configured for this block.</p>
                                                            ) : (
                                                                <Table striped bordered hover size="sm" className="m-0">
                                                                    <thead className="table-light">
                                                                        <tr>
                                                                            <th className="text-center" style={{ width: '20%' }}>Row Number</th>
                                                                            <th className="text-center" style={{ width: '30%' }}>Row Length (feet)</th>
                                                                            <th className="text-center" style={{ width: '25%' }}>Vine Spacing</th>
                                                                            <th className="text-center" style={{ width: '25%' }}>Calculated Vines count</th>
                                                                        </tr>
                                                                    </thead>
                                                                    <tbody>
                                                                        {block.rows.map((row, rIdx) => {
                                                                            const vinesCount = Math.floor(row.row_length / (block.vine_spacing || 1));
                                                                            return (
                                                                                <tr key={`r-idx-${rIdx}`}>
                                                                                    <td className="text-center font-weight-bold text-secondary">
                                                                                        Row #{row.row_number}
                                                                                    </td>
                                                                                    <td className="text-center">
                                                                                        {row.row_length} ft
                                                                                    </td>
                                                                                    <td className="text-center text-muted">
                                                                                        {block.vine_spacing} ft
                                                                                    </td>
                                                                                    <td className="text-center text-primary font-weight-bold">
                                                                                        {vinesCount} vines
                                                                                    </td>
                                                                                </tr>
                                                                            );
                                                                        })}
                                                                    </tbody>
                                                                </Table>
                                                            )}
                                                        </div>
                                                    </td>
                                                </tr>
                                            )}
                                        </React.Fragment>
                                    );
                                })}
                            </tbody>
                        </Table>
                    )}
                </Card.Body>
            </Card>

            {/* Modal for adding/editing block */}
            <Modal show={showModal} onHide={handleClose} size="lg" backdrop="static">
                <Form onSubmit={handleSubmit}>
                    <Modal.Header closeButton className="bg-dark text-white">
                        <Modal.Title>{isEdit ? 'Edit Vineyard Block' : 'Add Vineyard Block'}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        {errorMsg && <div className="alert alert-danger py-2">{errorMsg}</div>}
                        
                        <h5 className="mb-3 text-secondary">Block Details</h5>
                        <Row>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Block Code</Form.Label>
                                    <Form.Control 
                                        type="text" 
                                        name="block_code" 
                                        value={formData.block_code} 
                                        onChange={handleChange} 
                                        disabled={isEdit} 
                                        placeholder="e.g. cs" 
                                        required 
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Varieties / Grapes</Form.Label>
                                    <Form.Control 
                                        type="text" 
                                        name="varieties" 
                                        value={formData.varieties} 
                                        onChange={handleChange} 
                                        placeholder="e.g. Cabernet Sauvignon" 
                                        required 
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Acres</Form.Label>
                                    <Form.Control 
                                        type="number" 
                                        step="0.01" 
                                        name="acres" 
                                        value={formData.acres} 
                                        onChange={handleChange} 
                                        required 
                                    />
                                </Form.Group>
                            </Col>
                        </Row>

                        <Row>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Vine Spacing (ft)</Form.Label>
                                    <Form.Control 
                                        type="number" 
                                        step="0.1" 
                                        name="vine_spacing" 
                                        value={formData.vine_spacing} 
                                        onChange={handleChange} 
                                        required 
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Row Spacing (ft)</Form.Label>
                                    <Form.Control 
                                        type="number" 
                                        step="0.1" 
                                        name="row_spacing" 
                                        value={formData.row_spacing} 
                                        onChange={handleChange} 
                                        required 
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Trellis Type</Form.Label>
                                    <Form.Control 
                                        type="text" 
                                        name="trellis_type" 
                                        value={formData.trellis_type} 
                                        onChange={handleChange} 
                                        placeholder="e.g. VSP" 
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={3}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Rootstock</Form.Label>
                                    <Form.Control 
                                        type="text" 
                                        name="rootstock" 
                                        value={formData.rootstock} 
                                        onChange={handleChange} 
                                        placeholder="e.g. 3309C" 
                                    />
                                </Form.Group>
                            </Col>
                        </Row>

                        <hr className="my-4" />

                        {/* Rows Configurator */}
                        <div className="d-flex justify-content-between align-items-center mb-3">
                            <h5 className="m-0 text-secondary">Rows Configuration</h5>
                            <Button variant="outline-success" size="sm" onClick={addRow}>
                                + Add Individual Row
                            </Button>
                        </div>

                        {/* Bulk Row Generator Widget */}
                        <div className="bg-light border rounded p-3 mb-3">
                            <h6 className="m-0 mb-2 text-dark font-weight-bold">Bulk Row Generator</h6>
                            <Row className="align-items-end">
                                <Col md={4}>
                                    <Form.Group className="mb-2">
                                        <Form.Label className="small mb-1">Number of Rows</Form.Label>
                                        <Form.Control 
                                            type="number" 
                                            value={genNumRows} 
                                            onChange={(e) => setGenNumRows(parseInt(e.target.value) || 0)} 
                                        />
                                    </Form.Group>
                                </Col>
                                <Col md={4}>
                                    <Form.Group className="mb-2">
                                        <Form.Label className="small mb-1">Length of Rows (feet)</Form.Label>
                                        <Form.Control 
                                            type="number" 
                                            value={genRowLength} 
                                            onChange={(e) => setGenRowLength(parseFloat(e.target.value) || 0)} 
                                        />
                                    </Form.Group>
                                </Col>
                                <Col md={4}>
                                    <Button variant="dark" className="w-100 mb-2" onClick={generateRowsBulk}>
                                        Generate &amp; Replace Rows
                                    </Button>
                                </Col>
                            </Row>
                        </div>

                        <div style={{ maxHeight: '250px', overflowY: 'auto' }}>
                            {formData.rows.length === 0 ? (
                                <p className="text-muted italic text-center p-3">No rows added yet. Use the bulk generator or click Add Row.</p>
                            ) : (
                                <Table striped bordered size="sm" className="align-middle">
                                    <thead className="table-light">
                                        <tr>
                                            <th className="text-center" style={{ width: '25%' }}>Row Number</th>
                                            <th className="text-center" style={{ width: '40%' }}>Row Length (ft)</th>
                                            <th className="text-center" style={{ width: '25%' }}>Vines Count (calc)</th>
                                            <th className="text-center" style={{ width: '10%' }}>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {formData.rows.map((row, index) => {
                                            const vCount = Math.floor(row.row_length / (formData.vine_spacing || 1));
                                            return (
                                                <tr key={`edit-row-${index}`}>
                                                    <td>
                                                        <Form.Control 
                                                            type="number" 
                                                            size="sm" 
                                                            value={row.row_number} 
                                                            onChange={(e) => handleRowChange(index, 'row_number', e.target.value)} 
                                                            required 
                                                        />
                                                    </td>
                                                    <td>
                                                        <InputGroup size="sm">
                                                            <Form.Control 
                                                                type="number" 
                                                                step="0.1" 
                                                                value={row.row_length} 
                                                                onChange={(e) => handleRowChange(index, 'row_length', e.target.value)} 
                                                                required 
                                                            />
                                                            <InputGroup.Text>ft</InputGroup.Text>
                                                        </InputGroup>
                                                    </td>
                                                    <td className="text-center text-primary font-weight-bold">
                                                        {vCount} vines
                                                    </td>
                                                    <td className="text-center">
                                                        <Button variant="danger" size="sm" onClick={() => removeRow(index)}>
                                                            🗑
                                                        </Button>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </Table>
                            )}
                        </div>
                    </Modal.Body>
                    <Modal.Header className="d-flex justify-content-end p-3 bg-light border-top">
                        <Button variant="secondary" className="me-2" onClick={handleClose}>
                            Cancel
                        </Button>
                        <Button variant="success" type="submit">
                            Save Vineyard Block
                        </Button>
                    </Modal.Header>
                </Form>
            </Modal>
        </Container>
    );
};

export default VineyardBlocks;
