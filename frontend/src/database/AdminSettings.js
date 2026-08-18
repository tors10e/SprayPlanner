import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import Header from "../components/header";
import NavBar from "../components/navbar";
import Footer from "../components/footer";
import ReactGA from 'react-ga4';

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:5001/api/settings' : '/api/settings';

const AdminSettings = () => {
    ReactGA.send({ hitType: "pageview", page: "/admin", title: "Admin Settings" });

    const [settings, setSettings] = useState({
        min_spray_interval: '7',
        max_spray_interval: '14',
        rain_threshold_inch: '1.0',
        min_rain_free_hours: '12',
        weather_provider: 'NOAA',
        wunderground_api_key: '',
        wunderground_station_id: 'KGALAKEM20'
    });
    const [loading, setLoading] = useState(true);
    const [statusMsg, setStatusMsg] = useState('');
    const [statusType, setStatusType] = useState('success');

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        setLoading(true);
        try {
            const response = await fetch(API_BASE);
            if (response.ok) {
                const data = await response.json();
                setSettings(prev => ({
                    ...prev,
                    ...data
                }));
            }
        } catch (error) {
            console.error("Error fetching settings:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setSettings(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatusMsg('');
        try {
            const response = await fetch(API_BASE, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            if (response.ok) {
                setStatusType('success');
                setStatusMsg('Settings saved successfully!');
            } else {
                setStatusType('danger');
                setStatusMsg('Error saving settings.');
            }
        } catch (error) {
            setStatusType('danger');
            setStatusMsg('Network error saving settings.');
        }
    };

    return (
        <Container fluid className="px-0 w-100">
            <Row><Header /></Row>
            <Row className="navbar"><NavBar /></Row>

            <Container fluid className="py-4 px-md-5" style={{ maxWidth: '800px' }}>
                <div className="mb-4">
                    <h1 className="h2 m-0 text-dark">Admin Settings</h1>
                    <p className="text-secondary m-0">Configure dynamic spray recommendation weather parameters and API keys.</p>
                </div>

                {statusMsg && (
                    <Alert variant={statusType} className="mb-4 py-2" onClose={() => setStatusMsg('')} dismissible>
                        {statusMsg}
                    </Alert>
                )}

                {loading ? (
                    <div className="p-5 text-center text-secondary">Loading settings...</div>
                ) : (
                    <Card className="border-0 shadow-sm w-100">
                        <Card.Header className="bg-dark text-white py-3">
                            <h5 className="m-0">Recommendation Settings</h5>
                        </Card.Header>
                        <Card.Body className="p-4">
                            <Form onSubmit={handleSubmit}>
                                <h6 className="text-primary border-bottom pb-2 mb-3">Spray Interval Rules</h6>
                                <Row>
                                    <Col md={6}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Minimum Spray Interval (Days)</Form.Label>
                                            <Form.Control 
                                                type="number"
                                                name="min_spray_interval"
                                                value={settings.min_spray_interval}
                                                onChange={handleChange}
                                                required
                                                min="1"
                                            />
                                            <Form.Text className="text-muted">
                                                Minimum days required between sprays.
                                            </Form.Text>
                                        </Form.Group>
                                    </Col>
                                    <Col md={6}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Maximum Spray Interval (Days)</Form.Label>
                                            <Form.Control 
                                                type="number"
                                                name="max_spray_interval"
                                                value={settings.max_spray_interval}
                                                onChange={handleChange}
                                                required
                                                min="1"
                                            />
                                            <Form.Text className="text-muted">
                                                Maximum days to allow if conditions are completely dry.
                                            </Form.Text>
                                        </Form.Group>
                                    </Col>
                                </Row>

                                <h6 className="text-primary border-bottom pb-2 mb-3 mt-3">Precipitation Rules</h6>
                                <Row>
                                    <Col md={6}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Rain Accumulation Threshold (Inches)</Form.Label>
                                            <Form.Control 
                                                type="number"
                                                step="0.01"
                                                name="rain_threshold_inch"
                                                value={settings.rain_threshold_inch}
                                                onChange={handleChange}
                                                required
                                                min="0.01"
                                            />
                                            <Form.Text className="text-muted">
                                                Cumulative rain since last spray that triggers a new spray recommendation.
                                            </Form.Text>
                                        </Form.Group>
                                    </Col>
                                    <Col md={6}>
                                        <Form.Group className="mb-3">
                                            <Form.Label>Minimum Rain-free Window (Hours)</Form.Label>
                                            <Form.Control 
                                                type="number"
                                                name="min_rain_free_hours"
                                                value={settings.min_rain_free_hours}
                                                onChange={handleChange}
                                                required
                                                min="1"
                                            />
                                            <Form.Text className="text-muted">
                                                Dry period required before spray can be applied.
                                            </Form.Text>
                                        </Form.Group>
                                    </Col>
                                </Row>

                                <h6 className="text-primary border-bottom pb-2 mb-3 mt-3">Weather Provider Configurations</h6>
                                <Form.Group className="mb-3">
                                    <Form.Label>Primary Forecast Provider</Form.Label>
                                    <Form.Select 
                                        name="weather_provider"
                                        value={settings.weather_provider}
                                        onChange={handleChange}
                                    >
                                        <option value="NOAA">NOAA (Free & Keyless Grid Forecast)</option>
                                        <option value="Weather Underground">Weather Underground (Personal Weather Station)</option>
                                    </Form.Select>
                                </Form.Group>

                                {settings.weather_provider === 'Weather Underground' && (
                                    <Row className="bg-light border rounded p-3 mb-3 mx-0">
                                        <Col md={6}>
                                            <Form.Group className="mb-3">
                                                <Form.Label>Weather Underground Station ID</Form.Label>
                                                <Form.Control 
                                                    type="text"
                                                    name="wunderground_station_id"
                                                    value={settings.wunderground_station_id}
                                                    onChange={handleChange}
                                                    placeholder="e.g. KGALAKEM20"
                                                    required
                                                />
                                            </Form.Group>
                                        </Col>
                                        <Col md={6}>
                                            <Form.Group className="mb-3">
                                                <Form.Label>WUnderground API Key</Form.Label>
                                                <Form.Control 
                                                    type="password"
                                                    name="wunderground_api_key"
                                                    value={settings.wunderground_api_key}
                                                    onChange={handleChange}
                                                    placeholder="Enter WUnderground API Key"
                                                />
                                            </Form.Group>
                                        </Col>
                                    </Row>
                                )}

                                <div className="d-flex justify-content-end mt-4">
                                    <Button variant="success" size="lg" type="submit" className="px-5 shadow-sm">
                                        Save Configurations
                                    </Button>
                                </div>
                            </Form>
                        </Card.Body>
                    </Card>
                )}
            </Container>
            <Row><Footer /></Row>
        </Container>
    );
};

export default AdminSettings;
