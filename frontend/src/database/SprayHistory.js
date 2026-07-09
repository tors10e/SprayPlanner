import React, { useState, useEffect } from 'react';
import { Container, Table, Button, Modal, Form, Row, Col, Card, Alert, Badge } from 'react-bootstrap';
import Header from "../components/header";
import NavBar from "../components/navbar";
import Footer from "../components/footer";
import ReactGA from "react-ga4";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5001/api/products";
const HISTORY_API = API_BASE.replace('/products', '/history');

const EMPTY_ROW = {
    "Pesticide": "",
    "EPA No": "",
    "Group": "",
    "Active Ingredient": "",
    "Singal Word": "",
    "REI (h)": "",
    "PHI (d)": "",
    "Units": "",
    "PHI Date": "",
    "REI_TIME": "",
    "Min Dose": "",
    "Max Dose": "",
    "Dose/acre": "",
    "Dose per L @150 l": "",
    "Rate Units": "",
    "Calculated Dose": "",
    "Dose Units": "",
    "Notes": ""
};

const EMPTY_HISTORY_FORM = {
    spray_number: "",
    block: "",
    date: "",
    end_time: "",
    liters_acre: "",
    event_id: null,
    block_event_id: null,
    rows: [{ ...EMPTY_ROW }]
};

const calculatePhiDate = (dateStr, phiDays) => {
    if (!dateStr || phiDays === null || phiDays === undefined || phiDays === "") return "";
    try {
        const parts = dateStr.split('/');
        if (parts.length !== 3) return "";
        const month = parseInt(parts[0], 10) - 1;
        const day = parseInt(parts[1], 10);
        let year = parseInt(parts[2], 10);
        if (year < 100) year += 2000;
        
        const date = new Date(year, month, day);
        date.setDate(date.getDate() + parseInt(phiDays, 10));
        
        return (date.getMonth() + 1) + '/' + date.getDate() + '/' + String(date.getFullYear()).slice(-2);
    } catch (e) {
        return "";
    }
};

const calculateReiTime = (endTimeStr, reiHours) => {
    if (!endTimeStr || reiHours === null || reiHours === undefined || reiHours === "") return "";
    try {
        if (endTimeStr.toLowerCase() === 'na' || endTimeStr.length !== 4) return "";
        const hours = parseInt(endTimeStr.slice(0, 2), 10);
        const minutes = parseInt(endTimeStr.slice(2, 4), 10);
        
        const totalHours = hours + parseInt(reiHours, 10);
        const finalHours = totalHours % 24;
        
        const pad = (num) => String(num).padStart(2, '0');
        return `${pad(finalHours)}${pad(minutes)}`;
    } catch (e) {
        return "";
    }
};

const SprayHistory = () => {
    ReactGA.send({ hitType: "pageview", page: "/history", title: "Spray History" });

    const [history, setHistory] = useState([]);
    const [products, setProducts] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [currentId, setCurrentId] = useState(null); // stores composite block event name or null
    const [formData, setFormData] = useState({ ...EMPTY_HISTORY_FORM });
    
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

    const handleShow = (group = null, event = null) => {
        if (group && event) {
            // Edit existing block event
            setCurrentId(event.blockEventId);
            setFormData({
                spray_number: group.sprayNumber || "",
                block: event.block || "",
                date: event.date || "",
                end_time: event.endTime || "",
                liters_acre: event.litersAcre || "",
                event_id: group.eventId,
                block_event_id: event.blockEventId,
                rows: event.items.map(item => ({ ...item }))
            });
        } else {
            // Add new spray event
            const nextSprayNum = history.reduce((max, item) => (item["Spray #"] && item["Spray #"] > max ? item["Spray #"] : max), 0) + 1;
            const today = new Date();
            const formattedDate = (today.getMonth() + 1) + '/' + today.getDate() + '/' + String(today.getFullYear()).slice(-2);
            
            setCurrentId(null);
            setFormData({
                ...EMPTY_HISTORY_FORM,
                spray_number: nextSprayNum,
                date: formattedDate
            });
        }
        setShowModal(true);
    };

    const handleShowSingle = (event) => {
        // Edit single unscheduled block event
        setCurrentId(event.blockEventId);
        setFormData({
            spray_number: "",
            block: event.block || "",
            date: event.date || "",
            end_time: event.endTime || "",
            liters_acre: event.litersAcre || "",
            event_id: null,
            block_event_id: event.blockEventId,
            rows: event.items.map(item => ({ ...item }))
        });
        setShowModal(true);
    };

    const handleClone = (group, event) => {
        // Open form with duplicated chemical rows, but empty block and time fields so user can clone easily
        setCurrentId(null);
        setFormData({
            spray_number: group ? (group.sprayNumber || "") : "",
            block: "",
            date: event.date || "",
            end_time: "",
            liters_acre: event.litersAcre || "",
            event_id: null,
            block_event_id: null,
            rows: event.items.map(item => {
                const rowCopy = { ...item };
                delete rowCopy.id; // remove database keys
                delete rowCopy.block_event_id;
                delete rowCopy.event_id;
                return rowCopy;
            })
        });
        setShowModal(true);
    };

    const handleClose = () => setShowModal(false);

    const handleHeaderChange = (e) => {
        const { name, value } = e.target;
        const updated = { ...formData, [name]: value };
        
        if (name === 'date' && formData.rows) {
            updated.rows = formData.rows.map(row => ({
                ...row,
                "PHI Date": calculatePhiDate(value, row["PHI (d)"])
            }));
        } else if (name === 'end_time' && formData.rows) {
            updated.rows = formData.rows.map(row => ({
                ...row,
                "REI_TIME": calculateReiTime(value, row["REI (h)"])
            }));
        }
        setFormData(updated);
    };

    const handleRowChange = (rowIndex, e) => {
        const { name, value } = e.target;
        const updatedRows = [...formData.rows];
        updatedRows[rowIndex] = {
            ...updatedRows[rowIndex],
            [name]: value
        };
        setFormData({ ...formData, rows: updatedRows });
    };

    const handleProductSelect = (rowIndex, e) => {
        const productName = e.target.value;
        const product = products.find(p => p.Product === productName);
        const updatedRows = [...formData.rows];
        
        if (product) {
            updatedRows[rowIndex] = {
                ...updatedRows[rowIndex],
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
                "Rate Units": product.units || '',
                "PHI Date": calculatePhiDate(formData.date, product.phi),
                "REI_TIME": calculateReiTime(formData.end_time, product.rei)
            };
        } else {
            updatedRows[rowIndex] = {
                ...updatedRows[rowIndex],
                "Pesticide": productName
            };
        }
        setFormData({ ...formData, rows: updatedRows });
    };

    const copyRow = (rowIndex) => {
        const rowToCopy = formData.rows[rowIndex];
        const updatedRows = [...formData.rows];
        const clonedRow = { ...rowToCopy };
        delete clonedRow.id; // clear primary key id so it inserts as new
        
        updatedRows.splice(rowIndex + 1, 0, clonedRow);
        setFormData({ ...formData, rows: updatedRows });
    };

    const removeRow = (rowIndex) => {
        const updatedRows = formData.rows.filter((_, idx) => idx !== rowIndex);
        setFormData({ ...formData, rows: updatedRows });
    };

    const addRow = () => {
        const updatedRows = [...formData.rows, { ...EMPTY_ROW }];
        setFormData({ ...formData, rows: updatedRows });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Prevent duplicate chemicals in the same block spray event
        const pesticides = formData.rows.map(r => r.Pesticide).filter(Boolean);
        const hasDuplicates = pesticides.length !== new Set(pesticides).size;
        if (hasDuplicates) {
            alert("Duplicate chemicals found in the mix. Please remove the duplicate rows before saving.");
            return;
        }
        
        const payload = {
            event_id: formData.event_id,
            block_event_id: formData.block_event_id,
            spray_number: formData.spray_number === "" ? null : Number(formData.spray_number),
            block: formData.block,
            date: formData.date,
            end_time: formData.end_time,
            liters_acre: formData.liters_acre === "" ? null : Number(formData.liters_acre),
            rows: formData.rows.map(row => {
                const cleanRow = { ...row };
                ["REI (h)", "PHI (d)", "Min Dose", "Max Dose", "Dose/acre", "Dose per L @150 l", "Calculated Dose"].forEach(key => {
                    let val = cleanRow[key];
                    cleanRow[key] = val === "" || val === null || val === undefined ? null : Number(val);
                });
                return cleanRow;
            })
        };

        try {
            const response = await fetch(`${HISTORY_API}/save_group`, {
                method: "POST",
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                alert("Block spray event saved successfully!");
                fetchHistory();
                handleClose();
            } else {
                const errorData = await response.text();
                alert("Error saving block event: " + response.status + " " + errorData);
            }
        } catch (error) {
            console.error("Error saving block event:", error);
            alert("Network error: " + error.message);
        }
    };

    const handleDeleteEvent = async (blockEventId, sprayNumber, block, date) => {
        const label = sprayNumber ? `Spray #${sprayNumber}, Block ${block}` : `Unscheduled Block ${block}`;
        if (window.confirm(`Are you sure you want to delete ${label} on ${date}?`)) {
            try {
                const response = await fetch(`${HISTORY_API}/delete_event`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ block_event_id: blockEventId })
                });
                if (response.ok) {
                    fetchHistory();
                } else {
                    alert("Error deleting event: " + response.statusText);
                }
            } catch (error) {
                console.error("Error deleting event:", error);
            }
        }
    };

    const handleUpdateSprayNumber = async (oldNumber, newNumber) => {
        if (!newNumber || isNaN(newNumber)) {
            alert("Please enter a valid number.");
            return;
        }
        try {
            const response = await fetch(`${HISTORY_API}/update_spray_number`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    old_number: Number(oldNumber),
                    new_number: Number(newNumber)
                })
            });
            if (response.ok) {
                fetchHistory();
            } else {
                const err = await response.text();
                alert("Error updating spray number: " + err);
            }
        } catch (error) {
            console.error("Error updating spray number:", error);
        }
    };
    const handleDeleteSprayGroup = async (sprayNumber, eventId) => {
        if (window.confirm(`Are you sure you want to delete the entire Spray #${sprayNumber} (including all of its block events and chemicals)?`)) {
            try {
                const response = await fetch(`${HISTORY_API}/delete_spray_group`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ event_id: eventId })
                });
                if (response.ok) {
                    fetchHistory();
                } else {
                    alert("Error deleting spray: " + response.statusText);
                }
            } catch (error) {
                console.error("Error deleting spray:", error);
            }
        }
    };

    const handleCloneSprayGroup = async (sprayNumber, eventId) => {
        const newNum = prompt(`Enter target Spray Number to clone the entire Spray #${sprayNumber} mix to:`, sprayNumber);
        if (newNum !== null && newNum.trim() !== "") {
            try {
                const response = await fetch(`${HISTORY_API}/clone_spray_group`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        source_event_id: eventId,
                        new_spray_number: Number(newNum)
                    })
                });
                if (response.ok) {
                    alert(`Successfully cloned Spray #${sprayNumber} to Spray #${newNum}!`);
                    fetchHistory();
                } else {
                    alert("Error cloning spray: " + response.statusText);
                }
            } catch (error) {
                console.error("Error cloning spray:", error);
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

    // Sub-grouping logic: group by Spray Number, then sub-group by Block Event (block + date + time)
    const getGroupedHistory = () => {
        const groups = {};
        const unscheduled = {};
        
        history.forEach(item => {
            const sprayNum = item["Spray #"];
            const block = item["Block "] || 'Unspecified';
            const date = item["Date"] || '';
            const endTime = item["End Time"] || '';
            const litersAcre = item["Liters/Acre"];
            const eventId = item["event_id"];
            const blockEventId = item["block_event_id"];
            
            if (sprayNum !== null && sprayNum !== undefined && sprayNum !== "") {
                const groupKey = `Event-${eventId}`;
                if (!groups[groupKey]) {
                    groups[groupKey] = {
                        eventId: eventId,
                        sprayNumber: sprayNum,
                        blockEvents: {}
                    };
                }
                
                const blockKey = `Block-${blockEventId}`;
                if (!groups[groupKey].blockEvents[blockKey]) {
                    groups[groupKey].blockEvents[blockKey] = {
                        blockEventId: blockEventId,
                        block: block,
                        date: date,
                        endTime: endTime,
                        litersAcre: litersAcre,
                        items: []
                    };
                }
                groups[groupKey].blockEvents[blockKey].items.push(item);
            } else {
                // Unscheduled entries grouped by blockEventId
                const blockKey = `Block-${blockEventId}`;
                if (!unscheduled[blockKey]) {
                    unscheduled[blockKey] = {
                        blockEventId: blockEventId,
                        block: block,
                        date: date,
                        endTime: endTime,
                        litersAcre: litersAcre,
                        items: []
                    };
                }
                unscheduled[blockKey].items.push(item);
            }
        });
        
        // Sort groups descending by spray number
        const sortedGroups = Object.values(groups).sort((a, b) => b.sprayNumber - a.sprayNumber).map(group => {
            // Sort block events alphabetically by block name
            const sortedEvents = Object.values(group.blockEvents).sort((a, b) => {
                if (a.block < b.block) return -1;
                if (a.block > b.block) return 1;
                return 0;
            });
            return {
                ...group,
                events: sortedEvents
            };
        });
        
        const sortedUnscheduled = Object.values(unscheduled).sort((a, b) => {
            return new Date(b.date) - new Date(a.date);
        });
        
        return { groups: sortedGroups, unscheduled: sortedUnscheduled };
    };

    const groupedData = getGroupedHistory();
    console.log("DEBUG [groupedData]:", groupedData);

    // Stats calculations
    const totalApplications = history.length;
    const treatedBlocks = new Set(history.map(h => h["Block "]).filter(Boolean)).size;
    const uniqueChemicals = new Set(history.map(h => h["Pesticide"]).filter(Boolean)).size;

    return (
        <Container fluid className="px-0 w-100">
            <Row><Header /></Row>
            <Row className="navbar"><NavBar /></Row>

            <div className="mt-4">
                <h2>Pesticide Application History</h2>
                
                {/* ── Summary KPIs ── */}
                <Row className="mb-4 mt-3">
                    <Col md={4}>
                        <Card className="text-center border-0 shadow-sm bg-light w-100">
                            <Card.Body>
                                <Card.Title className="text-secondary small uppercase">Total Logs</Card.Title>
                                <Card.Text className="h2 font-weight-bold text-primary">{totalApplications}</Card.Text>
                            </Card.Body>
                        </Card>
                    </Col>
                    <Col md={4}>
                        <Card className="text-center border-0 shadow-sm bg-light w-100">
                            <Card.Body>
                                <Card.Title className="text-secondary small uppercase">Blocks Treated</Card.Title>
                                <Card.Text className="h2 font-weight-bold text-success">{treatedBlocks}</Card.Text>
                            </Card.Body>
                        </Card>
                    </Col>
                    <Col md={4}>
                        <Card className="text-center border-0 shadow-sm bg-light w-100">
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
                        <Button variant="primary" onClick={() => handleShow()}>Add Spray Event</Button>
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

                {/* ── Scheduled Spray Runs ── */}
                <h4 className="mt-4 mb-3 text-secondary border-bottom pb-2">Scheduled Spray Events</h4>
                {groupedData.groups.length === 0 ? (
                    <p className="text-muted italic">No scheduled spray runs found.</p>
                ) : (
                    groupedData.groups.map(group => (
                        <div key={`spray-group-${group.sprayNumber}`} className="mb-5">
                            <div className="border-bottom pb-2 mb-3 mt-4 d-flex align-items-center">
                                <h3 className="text-primary m-0 d-inline-block">Spray #{group.sprayNumber}</h3>
                                <Button variant="outline-primary" size="sm" className="ms-3 py-0 px-2 align-baseline" style={{ fontSize: '12px' }} onClick={() => {
                                    const newNum = prompt(`Enter new Spray Number to renumber Spray #${group.sprayNumber}:`, group.sprayNumber);
                                    if (newNum !== null && newNum.trim() !== "" && Number(newNum) !== group.sprayNumber) {
                                        handleUpdateSprayNumber(group.sprayNumber, newNum);
                                    }
                                }}>Edit Spray</Button>
                                <Button variant="outline-success" size="sm" className="ms-2 py-0 px-2 align-baseline" style={{ fontSize: '12px' }} onClick={() => handleCloneSprayGroup(group.sprayNumber, group.eventId)}>
                                    Clone Spray
                                </Button>
                                <Button variant="outline-danger" size="sm" className="ms-2 py-0 px-2 align-baseline" style={{ fontSize: '12px' }} onClick={() => handleDeleteSprayGroup(group.sprayNumber, group.eventId)}>
                                    Delete Spray
                                </Button>
                            </div>
                            
                            {group.events.map(event => (
                                <Card key={`block-event-${group.sprayNumber}-${event.blockEventId}`} className="mb-4 border shadow-sm w-100">
                                    <Card.Header className="bg-dark text-white d-flex justify-content-between align-items-center py-2">
                                        <div>
                                            <span className="h5 me-3 align-middle text-info">Block: {event.block}</span>
                                            <span className="badge bg-secondary me-2">Date: {event.date}</span>
                                            {event.endTime && <span className="badge bg-info me-2">End Time: {event.endTime}</span>}
                                            <span className="badge bg-light text-dark me-2">{event.items.length} Chemicals</span>
                                            {event.litersAcre && <span className="badge bg-warning text-dark">{event.litersAcre} L/Ac Water</span>}
                                        </div>
                                        <div>
                                            <Button variant="outline-success" size="sm" className="me-2 py-1" onClick={() => handleClone(group, event)}>Clone Event</Button>
                                            <Button variant="outline-light" size="sm" className="me-2 py-1" onClick={() => handleShow(group, event)}>Edit Event</Button>
                                            <Button variant="outline-danger" size="sm" className="py-1" onClick={() => handleDeleteEvent(event.blockEventId, group.sprayNumber, event.block, event.date)}>Delete Event</Button>
                                        </div>
                                    </Card.Header>
                                    <Card.Body className="p-0">
                                        <Table striped bordered hover responsive className="m-0 bg-white">
                                            <thead className="table-light">
                                                <tr>
                                                    <th>Pesticide</th>
                                                    <th>FRAC Group</th>
                                                    <th>Dose/acre</th>
                                                    <th>Notes</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {event.items.map((item, idx) => (
                                                    <tr key={`event-item-${idx}`}>
                                                        <td><strong>{item["Pesticide"] || '-'}</strong></td>
                                                        <td>
                                                            {item["Group"] ? (
                                                                <Badge bg="info" className="text-dark">FRAC {item["Group"]}</Badge>
                                                            ) : '-'}
                                                        </td>
                                                        <td>{item["Dose/acre"] ? `${item["Dose/acre"]} ${item["Rate Units"] || ''}` : '-'}</td>
                                                        <td><small className="text-muted">{item["Notes"]}</small></td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </Table>
                                    </Card.Body>
                                </Card>
                            ))}
                        </div>
                    ))
                )}

                {/* ── Unscheduled / Individual Sprays ── */}
                {groupedData.unscheduled.length > 0 && (
                    <div className="mt-5">
                        <h4 className="text-secondary border-bottom pb-2 mb-3">Individual &amp; Unscheduled Block Sprays</h4>
                        {groupedData.unscheduled.map(event => (
                            <Card key={`unscheduled-event-${event.blockEventId}`} className="mb-4 border shadow-sm w-100">
                                <Card.Header className="bg-secondary text-white d-flex justify-content-between align-items-center py-2">
                                    <div>
                                        <span className="h5 me-3 align-middle text-warning">Block: {event.block}</span>
                                        <span className="badge bg-light text-dark me-2">Date: {event.date}</span>
                                        {event.endTime && <span className="badge bg-dark me-2">End Time: {event.endTime}</span>}
                                        <span className="badge bg-white text-dark me-2">{event.items.length} Chemicals</span>
                                        {event.litersAcre && <span className="badge bg-warning text-dark">{event.litersAcre} L/Ac Water</span>}
                                    </div>
                                    <div>
                                        <Button variant="outline-success" size="sm" className="me-2 py-1 text-white border-white" onClick={() => handleClone(null, event)}>Clone Event</Button>
                                        <Button variant="outline-light" size="sm" className="me-2 py-1" onClick={() => handleShowSingle(event)}>Edit Event</Button>
                                        <Button variant="outline-danger" size="sm" className="py-1 text-white border-danger bg-danger" onClick={() => handleDeleteEvent(event.blockEventId, null, event.block, event.date)}>Delete Event</Button>
                                    </div>
                                </Card.Header>
                                <Card.Body className="p-0">
                                    <Table striped bordered hover responsive className="m-0 bg-white">
                                        <thead className="table-light">
                                            <tr>
                                                <th>Pesticide</th>
                                                <th>FRAC Group</th>
                                                <th>Dose/acre</th>
                                                <th>Notes</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {event.items.map((item, idx) => (
                                                <tr key={`unscheduled-item-${idx}`}>
                                                    <td><strong>{item["Pesticide"] || '-'}</strong></td>
                                                    <td>
                                                        {item["Group"] ? (
                                                            <Badge bg="info" className="text-dark">FRAC {item["Group"]}</Badge>
                                                        ) : '-'}
                                                    </td>
                                                    <td>{item["Dose/acre"] ? `${item["Dose/acre"]} ${item["Rate Units"] || ''}` : '-'}</td>
                                                    <td><small className="text-muted">{item["Notes"]}</small></td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </Table>
                                </Card.Body>
                            </Card>
                        ))}
                    </div>
                )}
            </div>

            {/* ── CRUD Modal ── */}
            <Modal show={showModal} onHide={handleClose} size="xl" backdrop="static">
                <Modal.Header closeButton>
                    <Modal.Title>{currentId ? "Edit Block Spray Run" : "Add Block Spray Run"}</Modal.Title>
                </Modal.Header>
                <Modal.Body style={{ maxHeight: 'calc(100vh - 210px)', overflowY: 'auto' }} className="bg-light">
                    <Form onSubmit={handleSubmit}>
                        
                        {/* ── Header Details ── */}
                        <Card className="mb-4 border-0 shadow-sm w-100">
                            <Card.Body>
                                <h5>Block Event Configuration</h5>
                                <Row>
                                    <Col md={2}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Spray #</Form.Label>
                                            <Form.Control type="number" placeholder="leave blank if Unscheduled" name="spray_number" value={formData.spray_number} onChange={handleHeaderChange} />
                                        </Form.Group>
                                    </Col>
                                    <Col md={2}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Block Code</Form.Label>
                                            <Form.Control type="text" placeholder="e.g. cs, pm, tr" name="block" value={formData.block} onChange={handleHeaderChange} required />
                                        </Form.Group>
                                    </Col>
                                    <Col md={2}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Date</Form.Label>
                                            <Form.Control type="text" placeholder="MM/DD/YY" name="date" value={formData.date} onChange={handleHeaderChange} required />
                                        </Form.Group>
                                    </Col>
                                    <Col md={2}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>End Time</Form.Label>
                                            <Form.Control type="text" placeholder="HHMM or NA" name="end_time" value={formData.end_time} onChange={handleHeaderChange} />
                                        </Form.Group>
                                    </Col>
                                    <Col md={4}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Water (Liters/Acre)</Form.Label>
                                            <Form.Control type="number" step="any" placeholder="e.g. 150" name="liters_acre" value={formData.liters_acre} onChange={handleHeaderChange} />
                                        </Form.Group>
                                    </Col>
                                </Row>
                            </Card.Body>
                        </Card>

                        {/* ── Dynamic Rows List ── */}
                        <div className="d-flex justify-content-between align-items-center mb-3">
                            <h5 className="m-0">Chemicals In Mix</h5>
                            <Button variant="outline-primary" size="sm" onClick={addRow}>+ Add Chemical</Button>
                        </div>

                        {formData.rows && formData.rows.map((row, idx) => (
                            <Card key={`form-row-${idx}`} className="mb-3 border shadow-sm w-100">
                                <Card.Header className="bg-white d-flex justify-content-between align-items-center py-2">
                                    <span className="font-weight-bold text-secondary small">Chemical #{idx + 1}</span>
                                    <div>
                                        <Button variant="outline-secondary" size="sm" className="me-2 py-0 px-2" style={{ fontSize: '12px' }} onClick={() => copyRow(idx)}>Copy Row</Button>
                                        {formData.rows.length > 1 && (
                                            <Button variant="outline-danger" size="sm" className="py-0 px-2" style={{ fontSize: '12px' }} onClick={() => removeRow(idx)}>Remove</Button>
                                        )}
                                    </div>
                                </Card.Header>
                                <Card.Body className="p-3">
                                    <Row>
                                        <Col md={9}>
                                            <Form.Group className="mb-2">
                                                <Form.Label className="small mb-1">Product</Form.Label>
                                                <Form.Select value={row["Pesticide"] || ''} onChange={(e) => handleProductSelect(idx, e)} required>
                                                    <option value="">-- Select Product --</option>
                                                    {products.map(p => (
                                                        <option key={p.Product} value={p.Product}>{p.Product}</option>
                                                    ))}
                                                </Form.Select>
                                            </Form.Group>
                                        </Col>
                                        <Col md={3}>
                                            <Form.Group className="mb-2">
                                                <Form.Label className="small mb-1">Dose/Acre</Form.Label>
                                                <Form.Control type="number" step="0.001" placeholder="Dose" name="Dose/acre" value={row["Dose/acre"] ?? ''} onChange={(e) => handleRowChange(idx, e)} />
                                            </Form.Group>
                                        </Col>
                                    </Row>
                                    <Row className="mt-2">
                                        <Col md={12}>
                                            <Form.Group className="mb-0">
                                                <Form.Control type="text" placeholder="Application notes..." name="Notes" value={row["Notes"] || ''} onChange={(e) => handleRowChange(idx, e)} />
                                            </Form.Group>
                                        </Col>
                                    </Row>
                                    {row["Pesticide"] && (
                                        <div className="mt-2 p-2 rounded bg-light border small text-muted d-flex justify-content-between flex-wrap gap-2">
                                            <span><strong>EPA:</strong> {row["EPA No"] || 'N/A'}</span>
                                            <span><strong>Group/FRAC:</strong> {row["Group"] || 'N/A'}</span>
                                            <span><strong>Active Ingredient:</strong> {row["Active Ingredient"] || 'N/A'}</span>
                                            <span><strong>Signal Word:</strong> {row["Singal Word"] || 'N/A'}</span>
                                            <span><strong>REI:</strong> {row["REI (h)"] || 0}h (Clear: {row["REI_TIME"] || 'N/A'})</span>
                                            <span><strong>PHI:</strong> {row["PHI (d)"] || 0}d (Clear: {row["PHI Date"] || 'N/A'})</span>
                                            <span><strong>Rate:</strong> {row["Min Dose"] || 0} - {row["Max Dose"] || 0} {row["Units"]}</span>
                                        </div>
                                    )}
                                </Card.Body>
                            </Card>
                        ))}

                        <div className="text-end mt-4">
                            <Button variant="secondary" className="me-2" onClick={handleClose}>Cancel</Button>
                            <Button variant="primary" type="submit">Save Block Event</Button>
                        </div>
                    </Form>
                </Modal.Body>
            </Modal>

            <Row><Footer /></Row>
        </Container>
    );
};

export default SprayHistory;
