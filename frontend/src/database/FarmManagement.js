import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Badge, Spinner, Modal } from 'react-bootstrap';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import Header from "../components/header";
import NavBar from "../components/navbar";
import Footer from "../components/footer";
import ReactGA from 'react-ga4';

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:5001/api' : '/api';

const FarmManagement = () => {
    ReactGA.send({ hitType: "pageview", page: "/farm", title: "Farm Management" });

    // Farm data states
    const [farmName, setFarmName] = useState('Terra Incognita Vineyard');
    const [acres, setAcres] = useState(0);
    const [farmArea, setFarmArea] = useState([]);
    
    // Saved baseline data for cancellation and dirty checking
    const [savedData, setSavedData] = useState(null);

    // Edit Mode state (default is FALSE - view/locked mode)
    const [isEditing, setIsEditing] = useState(false);

    // UI states
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [statusMsg, setStatusMsg] = useState({ type: '', text: '' });

    // Show vineyard blocks in the background
    const [showBlocks, setShowBlocks] = useState(true);
    const [blocks, setBlocks] = useState([]);

    // Unsaved changes modal state
    const [showUnsavedModal, setShowUnsavedModal] = useState(false);

    // Map and layer refs
    const mapRef = useRef(null);
    const farmPolygonRef = useRef(null);
    const markersGroupRef = useRef(null);
    const blocksLayerGroupRef = useRef(null);
    const fileInputRef = useRef(null);

    // Vertex marker icon (only shown in edit mode)
    const vertexIcon = L.divIcon({
        className: 'farm-vertex-icon',
        html: '<div style="width: 14px; height: 14px; background-color: #ffc107; border: 2px solid #000; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.8); cursor: pointer;"></div>',
        iconSize: [14, 14],
        iconAnchor: [7, 7]
    });

    useEffect(() => {
        fetchFarm();
        fetchBlocks();
    }, []);

    // Safe extraction of lat / lng whether array [lat, lng] or object { lat, lng }
    const getLat = (pt) => {
        if (!pt) return 0;
        if (Array.isArray(pt)) return pt[0];
        return pt.lat ?? pt.latitude ?? 0;
    };

    const getLng = (pt) => {
        if (!pt) return 0;
        if (Array.isArray(pt)) return pt[1];
        return pt.lng ?? pt.lon ?? pt.longitude ?? 0;
    };

    // Shoelace geodesic area calculation (returns 0 by default when < 3 vertices)
    const calculateAcresFromCoords = (coords) => {
        if (!coords || !Array.isArray(coords) || coords.length < 3) return 0;
        try {
            const refLat = getLat(coords[0]);
            const refLng = getLng(coords[0]);
            const meters = coords.map(p => {
                const lat = getLat(p);
                const lng = getLng(p);
                const x = (lng - refLng) * 111320 * Math.cos(refLat * Math.PI / 180);
                const y = (lat - refLat) * 111320;
                return [x, y];
            });
            let area = 0;
            for (let i = 0; i < meters.length; i++) {
                const p1 = meters[i];
                const p2 = meters[(i + 1) % meters.length];
                area += (p1[0] * p2[1]) - (p2[0] * p1[1]);
            }
            const calculated = Math.abs(area / 2) / 4046.8564;
            return isNaN(calculated) ? 0 : calculated;
        } catch (e) {
            console.error("Error calculating acres:", e);
            return 0;
        }
    };

    const fetchFarm = async () => {
        setLoading(true);
        try {
            const resp = await fetch(`${API_BASE}/farm`);
            if (resp.ok) {
                const data = await resp.json();
                const name = data.name || 'Terra Incognita Vineyard';
                const area = Array.isArray(data.farm_area) ? data.farm_area : [];
                let farmAcres = (typeof data.acres === 'number' && !isNaN(data.acres)) ? data.acres : 0;

                // If acres was 0 or unpopulated but we have vertices, compute it
                if (farmAcres === 0 && area.length >= 3) {
                    farmAcres = parseFloat(calculateAcresFromCoords(area).toFixed(2));
                }

                setFarmName(name);
                setFarmArea(area);
                setAcres(farmAcres);

                const snapshot = {
                    name,
                    acres: farmAcres,
                    farm_area: area ? JSON.parse(JSON.stringify(area)) : []
                };
                setSavedData(snapshot);
            }
        } catch (err) {
            console.error("Error fetching farm profile:", err);
            setStatusMsg({ type: 'danger', text: 'Error connecting to server to load farm data.' });
        } finally {
            setLoading(false);
        }
    };

    const fetchBlocks = async () => {
        try {
            const resp = await fetch(`${API_BASE}/blocks`);
            if (resp.ok) {
                const data = await resp.json();
                setBlocks(data || []);
            }
        } catch (err) {
            console.error("Error fetching vineyard blocks:", err);
        }
    };

    // Dirty checking against saved baseline
    const isFormDirty = () => {
        if (!savedData) return false;
        const current = {
            name: farmName,
            acres,
            farm_area: farmArea
        };
        return JSON.stringify(current) !== JSON.stringify(savedData);
    };

    // Initialize Leaflet Map
    useEffect(() => {
        if (loading) return;

        const container = document.getElementById('farm-boundary-map');
        if (!container || mapRef.current) return;

        let mapCenter = [34.7333, -83.5026];
        let mapZoom = 16;

        if (farmArea && farmArea.length > 0) {
            let sumLat = 0, sumLng = 0;
            farmArea.forEach(p => { sumLat += getLat(p); sumLng += getLng(p); });
            mapCenter = [sumLat / farmArea.length, sumLng / farmArea.length];
        } else if (blocks.length > 0) {
            const blocksWithPoly = blocks.filter(b => b.block_area && b.block_area.length > 0);
            if (blocksWithPoly.length > 0) {
                let sumLat = 0, sumLng = 0, count = 0;
                blocksWithPoly.forEach(b => {
                    b.block_area.forEach(p => { sumLat += getLat(p); sumLng += getLng(p); count++; });
                });
                if (count > 0) mapCenter = [sumLat / count, sumLng / count];
            }
        }

        const map = L.map('farm-boundary-map', {
            zoomControl: true,
            scrollWheelZoom: true
        }).setView(mapCenter, mapZoom);

        mapRef.current = map;

        // Satellite imagery layer
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 19,
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, USDA, USGS'
        }).addTo(map);

        updateMapLayers(farmArea, isEditing);
        drawBlocksLayer();

        if (farmArea && farmArea.length >= 3) {
            map.fitBounds(L.latLngBounds(farmArea), { padding: [40, 40] });
        }

        return () => {
            if (mapRef.current) {
                mapRef.current.remove();
                mapRef.current = null;
                farmPolygonRef.current = null;
                markersGroupRef.current = null;
                blocksLayerGroupRef.current = null;
            }
        };
    }, [loading]);

    // Handle map resize on edit mode toggle
    useEffect(() => {
        if (mapRef.current) {
            setTimeout(() => {
                mapRef.current.invalidateSize();
            }, 200);
        }
    }, [isEditing]);

    // Handle window resize
    useEffect(() => {
        const handleResize = () => {
            if (mapRef.current) {
                mapRef.current.invalidateSize();
            }
        };
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    // Handle Map Click based on Edit Mode
    useEffect(() => {
        const map = mapRef.current;
        if (!map) return;

        // Click handler is ONLY active when isEditing is TRUE
        const handleMapClick = (e) => {
            if (!isEditing) return;
            const newPt = [parseFloat(e.latlng.lat.toFixed(6)), parseFloat(e.latlng.lng.toFixed(6))];
            setFarmArea(prev => [...prev, newPt]);
        };

        if (isEditing) {
            map.on('click', handleMapClick);
        } else {
            map.off('click');
        }

        return () => {
            map.off('click', handleMapClick);
        };
    }, [isEditing]);

    // Redraw blocks layer when showBlocks or blocks change
    useEffect(() => {
        drawBlocksLayer();
    }, [showBlocks, blocks]);

    const drawBlocksLayer = () => {
        const map = mapRef.current;
        if (!map) return;

        if (blocksLayerGroupRef.current) {
            map.removeLayer(blocksLayerGroupRef.current);
            blocksLayerGroupRef.current = null;
        }

        if (!showBlocks || !blocks || blocks.length === 0) return;

        const group = L.layerGroup().addTo(map);
        blocksLayerGroupRef.current = group;

        const colors = ['#007bff', '#28a745', '#dc3545', '#17a2b8', '#6610f2', '#e83e8c'];
        blocks.forEach((block, index) => {
            if (!block.block_area || block.block_area.length === 0) return;
            const color = colors[index % colors.length];
            const poly = L.polygon(block.block_area, {
                color: color,
                weight: 2,
                fillColor: color,
                fillOpacity: 0.35
            }).addTo(group);
            poly.bindTooltip(`Block ${block.block_code.toUpperCase()} (${block.varieties || ''})`, { sticky: true });
        });
    };

    // Update farm boundary polygon & vertex markers
    const updateMapLayers = (coords, editable) => {
        const map = mapRef.current;
        if (!map) return;

        if (farmPolygonRef.current) {
            map.removeLayer(farmPolygonRef.current);
            farmPolygonRef.current = null;
        }
        if (markersGroupRef.current) {
            map.removeLayer(markersGroupRef.current);
            markersGroupRef.current = null;
        }

        if (!coords || coords.length === 0) return;

        // OUTLINE ONLY with EMPTY INTERIOR as requested
        farmPolygonRef.current = L.polygon(coords, {
            color: '#ffc107',        // Vibrant gold outline
            weight: 3.5,            // Clean border width
            dashArray: editable ? '4, 4' : '8, 6', // Dotted during edit, dashed in display
            fill: false,            // Explicitly disable interior fill
            fillOpacity: 0.0        // Completely transparent interior
        }).addTo(map);

        // Vertex markers are ONLY created and displayed when editable is TRUE
        if (editable) {
            const markersGroup = L.layerGroup().addTo(map);
            markersGroupRef.current = markersGroup;

            coords.forEach((latlng, idx) => {
                const marker = L.marker(latlng, {
                    icon: vertexIcon,
                    draggable: true
                }).addTo(markersGroup);

                marker.bindTooltip(`Point ${idx + 1} (drag to move, dbl-click to delete)`, { direction: 'top' });

                marker.on('dragend', (e) => {
                    const newPos = e.target.getLatLng();
                    setFarmArea(prev => {
                        const updated = [...prev];
                        updated[idx] = [parseFloat(newPos.lat.toFixed(6)), parseFloat(newPos.lng.toFixed(6))];
                        return updated;
                    });
                });

                marker.on('dblclick', () => {
                    setFarmArea(prev => prev.filter((_, i) => i !== idx));
                });
            });
        }
    };

    // Synchronize layers and calculate acreage whenever farmArea or isEditing changes
    useEffect(() => {
        if (mapRef.current) {
            updateMapLayers(farmArea, isEditing);

            if (farmArea && farmArea.length >= 3) {
                const calcAcres = calculateAcresFromCoords(farmArea);
                setAcres(isNaN(calcAcres) ? 0 : parseFloat(calcAcres.toFixed(2)));
            } else {
                setAcres(0);
            }
        }
    }, [farmArea, isEditing]);

    // Undo last sketch point (Edit mode only)
    const undoLastPoint = () => {
        if (!isEditing) return;
        setFarmArea(prev => prev.slice(0, -1));
    };

    // Clear boundary (Edit mode only)
    const clearBoundary = () => {
        if (!isEditing) return;
        if (farmArea.length > 0 && !window.confirm("Are you sure you want to clear the boundary?")) {
            return;
        }
        setFarmArea([]);
        setAcres(0);
    };

    // Zoom to fit boundary or blocks
    const zoomToFit = () => {
        const map = mapRef.current;
        if (!map) return;

        if (farmArea && farmArea.length >= 3) {
            map.fitBounds(L.latLngBounds(farmArea), { padding: [40, 40] });
        } else if (blocks.length > 0) {
            const blocksWithPoly = blocks.filter(b => b.block_area && b.block_area.length > 0);
            if (blocksWithPoly.length > 0) {
                map.fitBounds(L.latLngBounds(blocksWithPoly.flatMap(b => b.block_area)), { padding: [40, 40] });
            }
        }
    };

    // Handle File Upload for Boundary (.kml, .kmz, .shp, .zip)
    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);
        setStatusMsg({ type: '', text: '' });

        const formData = new FormData();
        formData.append('file', file);

        try {
            const resp = await fetch(`${API_BASE}/farm/upload-boundary`, {
                method: 'POST',
                body: formData
            });

            const data = await resp.json();

            if (resp.ok && data.coordinates) {
                setFarmArea(data.coordinates);
                let fileAcres = (typeof data.acres === 'number' && !isNaN(data.acres)) ? data.acres : calculateAcresFromCoords(data.coordinates);
                if (isNaN(fileAcres)) fileAcres = 0;
                fileAcres = parseFloat(fileAcres.toFixed(2));
                setAcres(fileAcres);
                setStatusMsg({
                    type: 'success',
                    text: `Imported "${data.filename}" (${data.coordinates.length} vertices, ${fileAcres.toFixed(2)} acres). Click "Save Changes" to apply.`
                });

                if (mapRef.current && data.coordinates.length >= 3) {
                    mapRef.current.fitBounds(L.latLngBounds(data.coordinates), { padding: [40, 40] });
                }
            } else {
                setStatusMsg({
                    type: 'danger',
                    text: data.message || 'Error parsing file. Please ensure it contains polygon geometry in WGS84.'
                });
            }
        } catch (err) {
            console.error("Error uploading boundary file:", err);
            setStatusMsg({ type: 'danger', text: 'Network error: ' + err.message });
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    // Save Farm Changes
    const handleSave = async () => {
        if (!farmName.trim()) {
            setStatusMsg({ type: 'danger', text: 'Farm name is required.' });
            return false;
        }

        setSaving(true);
        setStatusMsg({ type: '', text: '' });

        const payload = {
            name: farmName.trim(),
            acres: (typeof acres === 'number' && !isNaN(acres)) ? acres : 0,
            farm_area: farmArea
        };

        try {
            const resp = await fetch(`${API_BASE}/farm`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const result = await resp.json();
            if (resp.ok) {
                setStatusMsg({ type: 'success', text: 'Farm profile and boundary saved successfully!' });
                setSavedData({
                    name: farmName.trim(),
                    acres: payload.acres,
                    farm_area: JSON.parse(JSON.stringify(farmArea))
                });
                setIsEditing(false); // Return to locked / view mode
                return true;
            } else {
                setStatusMsg({ type: 'danger', text: result.message || 'Error saving farm profile.' });
                return false;
            }
        } catch (err) {
            console.error("Error saving farm:", err);
            setStatusMsg({ type: 'danger', text: 'Network error saving farm: ' + err.message });
            return false;
        } finally {
            setSaving(false);
        }
    };

    // Cancel editing
    const handleCancelClick = () => {
        if (isFormDirty()) {
            setShowUnsavedModal(true);
        } else {
            setIsEditing(false);
        }
    };

    const handleConfirmDiscard = () => {
        if (savedData) {
            setFarmName(savedData.name);
            setAcres(savedData.acres);
            setFarmArea(JSON.parse(JSON.stringify(savedData.farm_area)));
        }
        setShowUnsavedModal(false);
        setIsEditing(false);
        setStatusMsg({ type: '', text: '' });
    };

    // Formatted acreage guarantee: always display numeric formatted string, never NaN
    const displayAcres = (typeof acres === 'number' && !isNaN(acres)) ? acres.toFixed(2) : '0.00';

    return (
        <Container fluid className="px-0 w-100 d-flex flex-column" style={{ minHeight: '100vh' }}>
            <Row><Header /></Row>
            <Row className="navbar"><NavBar /></Row>

            {/* Screen-filling container taking up most of the display */}
            <Container fluid className="px-3 px-md-4 py-2 flex-grow-1 d-flex flex-column">
                <div className="w-100 flex-grow-1 d-flex flex-column">
                    {statusMsg.text && (
                        <Alert variant={statusMsg.type} dismissible onClose={() => setStatusMsg({ type: '', text: '' })} className="py-2 mb-2 w-100">
                            {statusMsg.text}
                        </Alert>
                    )}

                    {loading ? (
                        <div className="text-center py-5 text-secondary flex-grow-1 d-flex flex-column justify-content-center align-items-center w-100">
                            <Spinner animation="border" className="mb-2" />
                            <div>Loading farm details...</div>
                        </div>
                    ) : (
                        <>
                            {/* Compact unified top control bar */}
                            <Card className="border-0 shadow-sm w-100 mb-2" style={{ width: '100%' }}>
                                <Card.Body className="py-2 px-3">
                                    <div className="d-flex flex-wrap justify-content-between align-items-center gap-3">
                                        
                                        {/* Left: Farm Name & Extent display */}
                                        <div className="d-flex align-items-center gap-3 flex-grow-1" style={{ minWidth: '300px' }}>
                                            {!isEditing ? (
                                                <div>
                                                    <div className="d-flex align-items-center gap-2">
                                                        <h4 className="m-0 text-dark fw-bold">{farmName}</h4>
                                                        <Badge bg="secondary" className="px-2 py-1" style={{ fontSize: '11px' }}>🔒 Locked</Badge>
                                                    </div>
                                                    <small className="text-muted">
                                                        {farmArea.length >= 3 ? `${farmArea.length} boundary points` : 'No boundary set'}
                                                    </small>
                                                </div>
                                            ) : (
                                                <div className="d-flex align-items-center gap-2 flex-grow-1" style={{ maxWidth: '420px' }}>
                                                    <Form.Control
                                                        type="text"
                                                        value={farmName}
                                                        onChange={(e) => setFarmName(e.target.value)}
                                                        placeholder="Enter farm name"
                                                        className="fw-bold form-control-sm"
                                                    />
                                                    <Badge bg="warning" text="dark" className="px-2 py-1 text-nowrap" style={{ fontSize: '11px' }}>
                                                        ✎ Editing
                                                    </Badge>
                                                </div>
                                            )}

                                            <div className="border-start ps-3 d-flex align-items-baseline gap-1">
                                                <span className="fs-4 fw-bold text-success">{displayAcres}</span>
                                                <span className="text-muted small fw-semibold">acres</span>
                                            </div>
                                        </div>

                                        {/* Right: Actions and Edit Controls */}
                                        <div className="d-flex flex-wrap align-items-center gap-2">
                                            <Form.Check 
                                            type="switch"
                                            id="toggle-blocks-display"
                                            label={<span className="small text-dark fw-semibold">Show Blocks</span>}
                                            checked={showBlocks}
                                            onChange={(e) => setShowBlocks(e.target.checked)}
                                            className="me-2"
                                        />
                                        <Button 
                                            variant="outline-secondary" 
                                            size="sm"
                                            onClick={zoomToFit}
                                            title="Fit map view to boundary or vineyard blocks"
                                        >
                                            🔍 Fit Map
                                        </Button>

                                        {!isEditing ? (
                                            <Button 
                                                variant="primary" 
                                                size="sm"
                                                className="shadow-sm px-3 fw-semibold"
                                                onClick={() => {
                                                    setIsEditing(true);
                                                    setStatusMsg({ type: '', text: '' });
                                                }}
                                            >
                                                ✏️ Edit Farm &amp; Boundary
                                            </Button>
                                        ) : (
                                            <>
                                                <input 
                                                    type="file" 
                                                    ref={fileInputRef} 
                                                    style={{ display: 'none' }} 
                                                    accept=".kml,.kmz,.shp,.zip" 
                                                    onChange={handleFileUpload} 
                                                />
                                                <Button 
                                                    variant="outline-dark" 
                                                    size="sm"
                                                    onClick={() => fileInputRef.current && fileInputRef.current.click()}
                                                    disabled={uploading}
                                                >
                                                    {uploading ? (
                                                        <>
                                                            <Spinner animation="border" size="sm" className="me-1" />
                                                            Importing...
                                                        </>
                                                    ) : (
                                                        "📁 Import KML / SHP / ZIP"
                                                    )}
                                                </Button>
                                                <Button 
                                                    variant="outline-secondary" 
                                                    size="sm"
                                                    onClick={undoLastPoint}
                                                    disabled={farmArea.length === 0}
                                                >
                                                    ↩ Undo Point
                                                </Button>
                                                <Button 
                                                    variant="outline-danger" 
                                                    size="sm"
                                                    onClick={clearBoundary}
                                                    disabled={farmArea.length === 0}
                                                >
                                                    🗑 Clear
                                                </Button>
                                                <div className="vr mx-1"></div>
                                                <Button 
                                                    variant="secondary" 
                                                    size="sm"
                                                    onClick={handleCancelClick}
                                                    disabled={saving}
                                                >
                                                    Cancel
                                                </Button>
                                                <Button 
                                                    variant="success" 
                                                    size="sm"
                                                    className="shadow-sm px-3 fw-semibold"
                                                    onClick={handleSave}
                                                    disabled={saving}
                                                >
                                                    {saving ? (
                                                        <>
                                                            <Spinner animation="border" size="sm" className="me-1" />
                                                            Saving...
                                                        </>
                                                    ) : (
                                                        "Save Changes"
                                                    )}
                                                </Button>
                                            </>
                                        )}
                                    </div>
                                </div>

                                {isEditing && (
                                    <div className="mt-2 pt-2 border-top d-flex flex-wrap justify-content-between align-items-center text-muted small">
                                        <span>💡 <strong>Edit mode active:</strong> Click on the map to add boundary outline points &bull; Drag yellow handles to adjust &bull; Double-click a point to remove it</span>
                                        <span><strong>{farmArea.length}</strong> points | <strong>{displayAcres}</strong> acres</span>
                                    </div>
                                )}
                            </Card.Body>
                        </Card>

                        {/* Large screen-filling Map Card */}
                        <Card className="border-0 shadow-sm w-100 flex-grow-1 position-relative d-flex flex-column" style={{ minHeight: '580px', width: '100%', marginBottom: '12px' }}>
                            <Card.Body className="p-0 position-relative flex-grow-1" style={{ height: 'calc(100vh - 215px)', minHeight: '580px' }}>
                                <div 
                                    id="farm-boundary-map" 
                                    style={{ 
                                        height: '100%', 
                                        width: '100%', 
                                        borderRadius: '0.375rem',
                                        cursor: isEditing ? 'crosshair' : 'default'
                                    }} 
                                />

                                {/* Subtle corner overlay badge on map */}
                                <div 
                                    className="position-absolute bg-white px-2 py-1 rounded shadow-sm small d-flex align-items-center gap-2"
                                    style={{ zIndex: 1000, bottom: '12px', left: '12px', opacity: 0.92 }}
                                >
                                    <span style={{ display: 'inline-block', width: '14px', height: '3px', backgroundColor: '#ffc107', border: '1px dashed #333' }}></span>
                                    <span className="text-dark fw-semibold" style={{ fontSize: '12px' }}>
                                        {farmArea.length >= 3 ? `${displayAcres} ac Property Outline` : "No boundary set (0.00 acres)"}
                                    </span>
                                    <span className="text-muted" style={{ fontSize: '11px' }}>
                                        {isEditing ? "(Editing)" : "(Locked)"}
                                    </span>
                                </div>
                            </Card.Body>
                        </Card>
                    </>
                )}
                </div>
            </Container>

            {/* ── Unsaved Changes Modal on Cancel ── */}
            <Modal show={showUnsavedModal} onHide={() => setShowUnsavedModal(false)} centered>
                <Modal.Header closeButton>
                    <Modal.Title>Unsaved Changes</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <p className="m-0">
                        You have unsaved changes to your farm boundary. Would you like to discard these changes and return to view mode?
                    </p>
                </Modal.Body>
                <Modal.Footer className="d-flex justify-content-between">
                    <Button variant="outline-danger" onClick={handleConfirmDiscard}>
                        Discard Changes
                    </Button>
                    <div>
                        <Button variant="secondary" className="me-2" onClick={() => setShowUnsavedModal(false)}>
                            Keep Editing
                        </Button>
                        <Button variant="success" onClick={async () => { const ok = await handleSave(); if (ok) setShowUnsavedModal(false); }}>
                            Save Changes
                        </Button>
                    </div>
                </Modal.Footer>
            </Modal>

            <Row className="mt-auto"><Footer /></Row>
        </Container>
    );
};

export default FarmManagement;
