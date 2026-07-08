import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Tabs, Tab, Table, Badge, Spinner, Alert } from 'react-bootstrap';
import Header from "../components/header";
import NavBar from "../components/navbar";
import Footer from "../components/footer";
import ReactGA from "react-ga4";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5001/api/products";
const PLANNER_API = API_BASE.replace('/products', '/planner/generate');

const SprayPlanner = () => {
    ReactGA.send({ hitType: "pageview", page: "/planner", title: "Spray Planner" });

    // Input States
    const [years, setYears] = useState({
        "2026": true,
        "2027": false,
        "2028": false
    });
    const [organicOnly, setOrganicOnly] = useState(false);
    const [interval, setInterval] = useState(14);
    const [startDate, setStartDate] = useState("04-01");
    const [endDate, setEndDate] = useState("10-20");
    const [totalAcres, setTotalAcres] = useState(10.0);

    // Response States
    const [loading, setLoading] = useState(false);
    const [plans, setPlans] = useState(null);
    const [error, setError] = useState(null);

    const handleYearCheckbox = (year) => {
        setYears(prev => ({
            ...prev,
            [year]: !prev[year]
        }));
    };

    const handleRunPlanner = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setPlans(null);

        const selectedYears = Object.keys(years).filter(y => years[y]).map(Number);
        if (selectedYears.length === 0) {
            setError("Please select at least one year to optimize.");
            setLoading(false);
            return;
        }

        const payload = {
            years: selectedYears,
            organic_only: organicOnly,
            default_interval: Number(interval),
            start_date_month_day: startDate,
            end_date_month_day: endDate,
            total_acres: Number(totalAcres)
        };

        try {
            const response = await fetch(PLANNER_API, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (response.ok) {
                setPlans(data.plans);
            } else {
                setError(data.message || "Failed to generate plan.");
            }
        } catch (err) {
            console.error("Planner generation error:", err);
            setError("Network error: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    // Helper to calculate statistics for a specific year's plan
    const getPlanStats = (yearPlan) => {
        if (!yearPlan || yearPlan.length === 0) return { cost: 0, count: 0, avg: 0, invalidCount: 0 };
        let cost = 0;
        let count = 0;
        let invalidCount = 0;

        yearPlan.forEach(event => {
            if (event.products) {
                cost += event["Total Cost"] || 0;
                count++;
            } else {
                invalidCount++;
            }
        });

        return {
            cost: cost.toFixed(2),
            count: yearPlan.length,
            avg: count > 0 ? (cost / count).toFixed(2) : 0,
            invalidCount
        };
    };

    return (
        <Container fluid className="px-0 w-100">
            <Row><Header /></Row>
            <Row className="navbar"><NavBar /></Row>

            <div className="mt-4">
                <h2>Seasonal Spray Planner</h2>
                <p className="text-muted">
                    Generate and simulate a cost-optimal chemical spray schedule across multiple years. 
                    The scheduler respects PHI limits, FRAC rotation policies, and growth stage specific weights automatically.
                </p>

                <Row className="mt-4">
                    {/* ── Left Column: Configuration Controls ── */}
                    <Col lg={4} className="mb-4">
                        <Card className="shadow-sm border-0 w-100">
                            <Card.Header className="bg-dark text-white font-weight-bold">
                                Optimization Settings
                            </Card.Header>
                            <Card.Body>
                                <Form onSubmit={handleRunPlanner}>
                                    {/* Years Checkboxes */}
                                    <Form.Group className="mb-3">
                                        <Form.Label className="font-weight-bold">Simulation Years</Form.Label>
                                        <div className="d-flex gap-3">
                                            {["2026", "2027", "2028"].map(yr => (
                                                <Form.Check 
                                                    key={yr}
                                                    type="checkbox"
                                                    id={`check-${yr}`}
                                                    label={yr}
                                                    checked={years[yr]}
                                                    onChange={() => handleYearCheckbox(yr)}
                                                />
                                            ))}
                                        </div>
                                    </Form.Group>

                                    {/* Dates */}
                                    <Row>
                                        <Col md={6}>
                                            <Form.Group className="mb-3">
                                                <Form.Label>Start Date (MM-DD)</Form.Label>
                                                <Form.Control type="text" value={startDate} onChange={(e) => setStartDate(e.target.value)} placeholder="04-01" required />
                                            </Form.Group>
                                        </Col>
                                        <Col md={6}>
                                            <Form.Group className="mb-3">
                                                <Form.Label>End Date (MM-DD)</Form.Label>
                                                <Form.Control type="text" value={endDate} onChange={(e) => setEndDate(e.target.value)} placeholder="10-20" required />
                                            </Form.Group>
                                        </Col>
                                    </Row>

                                    {/* Interval & Acres */}
                                    <Row>
                                        <Col md={6}>
                                            <Form.Group className="mb-3">
                                                <Form.Label>Interval (days)</Form.Label>
                                                <Form.Control type="number" min="1" value={interval} onChange={(e) => setInterval(e.target.value)} required />
                                            </Form.Group>
                                        </Col>
                                        <Col md={6}>
                                            <Form.Group className="mb-3">
                                                <Form.Label>Total Acres</Form.Label>
                                                <Form.Control type="number" step="0.1" min="0.1" value={totalAcres} onChange={(e) => setTotalAcres(e.target.value)} required />
                                            </Form.Group>
                                        </Col>
                                    </Row>

                                    {/* Organic Switch */}
                                    <Form.Group className="mb-4">
                                        <Form.Check 
                                            type="switch"
                                            id="organic-switch"
                                            label="Organic Only (OMRI Listed)"
                                            checked={organicOnly}
                                            onChange={(e) => setOrganicOnly(e.target.checked)}
                                        />
                                    </Form.Group>

                                    <Button variant="primary" type="submit" className="w-100 py-2" disabled={loading}>
                                        {loading ? (
                                            <>
                                                <Spinner as="span" animation="border" size="sm" role="status" className="me-2" />
                                                Optimizing Season...
                                            </>
                                        ) : "Run Simulation Planner"}
                                    </Button>
                                </Form>
                            </Card.Body>
                        </Card>
                    </Col>

                    {/* ── Right Column: Results Plan output ── */}
                    <Col lg={8} className="mb-4">
                        {error && <Alert variant="danger">{error}</Alert>}
                        
                        {loading && (
                            <Card className="text-center p-5 border-0 shadow-sm w-100 bg-white">
                                <Card.Body>
                                    <Spinner animation="grow" variant="primary" className="mb-3" />
                                    <h4>Simulating Spray Optimizer</h4>
                                    <p className="text-muted italic">Resolving cost functions, active chemical safety intervals, and rotating FRAC classes...</p>
                                </Card.Body>
                            </Card>
                        )}

                        {!loading && !plans && !error && (
                            <Card className="text-center p-5 border-dashed border-2 w-100">
                                <Card.Body className="text-muted">
                                    <i className="h1 bi bi-sliders mb-3 d-block text-secondary"></i>
                                    <h4>No Simulation Ran Yet</h4>
                                    <p>Configure parameters and click "Run Simulation Planner" to design and view season plans.</p>
                                </Card.Body>
                            </Card>
                        )}

                        {!loading && plans && (
                            <Card className="shadow-sm border-0 w-100">
                                <Card.Body className="p-3">
                                    <Tabs defaultActiveKey={Object.keys(plans)[0]} className="mb-4">
                                        {Object.keys(plans).map(year => {
                                            const yearPlan = plans[year];
                                            const stats = getPlanStats(yearPlan);

                                            return (
                                                <Tab eventKey={year} title={`${year} Plan`} key={year}>
                                                    {/* KPI Widgets for the Year */}
                                                    <Row className="mb-4">
                                                        <Col md={3}>
                                                            <div className="p-3 bg-light rounded text-center border">
                                                                <small className="text-secondary uppercase d-block mb-1">Total Cost</small>
                                                                <span className="h4 font-weight-bold text-success">${stats.cost}</span>
                                                            </div>
                                                        </Col>
                                                        <Col md={3}>
                                                            <div className="p-3 bg-light rounded text-center border">
                                                                <small className="text-secondary uppercase d-block mb-1">Applications</small>
                                                                <span className="h4 font-weight-bold text-primary">{stats.count}</span>
                                                            </div>
                                                        </Col>
                                                        <Col md={3}>
                                                            <div className="p-3 bg-light rounded text-center border">
                                                                <small className="text-secondary uppercase d-block mb-1">Avg cost/spray</small>
                                                                <span className="h4 font-weight-bold text-dark">${stats.avg}</span>
                                                            </div>
                                                        </Col>
                                                        <Col md={3}>
                                                            <div className="p-3 bg-light rounded text-center border">
                                                                <small className="text-secondary uppercase d-block mb-1">Gaps / Warnings</small>
                                                                <span className={`h4 font-weight-bold ${stats.invalidCount > 0 ? 'text-danger' : 'text-success'}`}>
                                                                    {stats.invalidCount}
                                                                </span>
                                                            </div>
                                                        </Col>
                                                    </Row>

                                                    {/* Event Schedule Table */}
                                                    <Table striped bordered hover responsive className="bg-white m-0">
                                                        <thead className="table-dark">
                                                            <tr>
                                                                <th>Date</th>
                                                                <th>Growth Stage</th>
                                                                <th>Pesticide Mix</th>
                                                                <th>FRAC Codes</th>
                                                                <th className="text-end">Cost/Dose</th>
                                                                <th className="text-end">Total Cost</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {yearPlan.map((event, idx) => {
                                                                const hasMix = event.products && event.products.length > 0;
                                                                return (
                                                                    <tr key={idx} className={hasMix ? "" : "table-danger"}>
                                                                        <td><strong>{event.date}</strong></td>
                                                                        <td><Badge bg="secondary">{event.stage}</Badge></td>
                                                                        <td>
                                                                            {hasMix ? (
                                                                                event.products.map(p => (
                                                                                    <Badge bg="primary" className="me-1 py-1 px-2" key={p}>{p}</Badge>
                                                                                ))
                                                                            ) : (
                                                                                <Badge bg="danger">NO VALID MIX FOUND</Badge>
                                                                            )}
                                                                        </td>
                                                                        <td>
                                                                            {hasMix && event.FRACs && event.FRACs.map(f => (
                                                                                <Badge bg="info" className="text-dark me-1" key={f}>FRAC {f}</Badge>
                                                                            ))}
                                                                        </td>
                                                                        <td className="text-end text-muted">
                                                                            {hasMix ? `$${(event["Cost/Dose"] || 0).toFixed(2)}` : "-"}
                                                                        </td>
                                                                        <td className="text-end font-weight-bold">
                                                                            {hasMix ? `$${(event["Total Cost"] || 0).toFixed(2)}` : "-"}
                                                                        </td>
                                                                    </tr>
                                                                );
                                                            })}
                                                        </tbody>
                                                    </Table>
                                                </Tab>
                                            );
                                        })}
                                    </Tabs>
                                </Card.Body>
                            </Card>
                        )}
                    </Col>
                </Row>
            </div>

            <Row><Footer /></Row>
        </Container>
    );
};

export default SprayPlanner;
