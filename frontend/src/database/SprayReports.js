import React, { useState, useEffect } from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Card from 'react-bootstrap/Card';
import Table from 'react-bootstrap/Table';
import Form from 'react-bootstrap/Form';
import Badge from 'react-bootstrap/Badge';
import Spinner from 'react-bootstrap/Spinner';
import TerraNavbar from '../components/navbar';

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:5001/api/history' : '/api/history';

function SprayReports() {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [timeRange, setTimeRange] = useState('past-year');
    const [expandedChems, setExpandedChems] = useState({});
    const [expandedBlocks, setExpandedBlocks] = useState({});
    const [expandedPhiBlocks, setExpandedPhiBlocks] = useState({});
    const [expandedReiBlocks, setExpandedReiBlocks] = useState({});

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await fetch(API_BASE);
            if (response.ok) {
                const data = await response.json();
                setHistory(data);
            }
        } catch (error) {
            console.error('Error fetching history:', error);
        } finally {
            setLoading(false);
        }
    };

    const parseDate = (dateStr) => {
        if (!dateStr) return null;
        // Clean string
        const cleanStr = String(dateStr).trim();
        
        // 1. Try slash delimiter (e.g. MM/DD/YYYY or MM/DD/YY)
        let parts = cleanStr.split('/');
        if (parts.length === 3) {
            const month = parseInt(parts[0], 10) - 1;
            const day = parseInt(parts[1], 10);
            let year = parseInt(parts[2], 10);
            if (year < 100) year += 2000;
            return new Date(year, month, day);
        }
        
        // 2. Try hyphen delimiter (e.g. YYYY-MM-DD or DD-MM-YYYY)
        parts = cleanStr.split('-');
        if (parts.length === 3) {
            if (parts[0].length === 4) {
                // YYYY-MM-DD
                const year = parseInt(parts[0], 10);
                const month = parseInt(parts[1], 10) - 1;
                const day = parseInt(parts[2], 10);
                return new Date(year, month, day);
            } else {
                // DD-MM-YYYY or MM-DD-YYYY - assume standard month/day
                const month = parseInt(parts[0], 10) - 1;
                const day = parseInt(parts[1], 10);
                let year = parseInt(parts[2], 10);
                if (year < 100) year += 2000;
                return new Date(year, month, day);
            }
        }
        
        // 3. Fallback: try browser native Date parsing
        const d = new Date(cleanStr);
        return isNaN(d.getTime()) ? null : d;
    };

    // Filter history based on time range
    const getFilteredHistory = () => {
        const now = new Date();
        
        return history.filter(item => {
            if (!item.Date) return false;
            const logDate = parseDate(item.Date);
            if (!logDate) return false;

            if (timeRange === 'past-year') {
                const oneYearAgo = new Date();
                oneYearAgo.setFullYear(now.getFullYear() - 1);
                return logDate >= oneYearAgo;
            } else if (timeRange === 'all-time') {
                return true;
            } else {
                // Calendar year check (e.g. 2026)
                const targetYear = parseInt(timeRange, 10);
                return logDate.getFullYear() === targetYear;
            }
        });
    };

    const filteredLogs = getFilteredHistory();

    // Grouping and aggregation logic
    const getReportsData = () => {
        // Group by (Pesticide, Rate Units) to prevent unit mixing
        const grouped = {};

        filteredLogs.forEach(item => {
            const chem = item.Pesticide || 'Unknown Product';
            const unit = item.Units || item["Rate Units"] || 'L';
            const key = `${chem}-${unit}`;

            const dose = item["Dose/acre"] || 0;
            const calcDose = item["Calculated Dose"] || 0;
            const calcDoseUnit = item["Dose Units"] || '';
            const campaign = item["Spray #"];
            const blockEventId = item.block_event_id;
            const block = item["Block "] || '';
            const date = item["Date"] || '';
            const endTime = item["End Time"] || '';
            const litersAcre = item["Liters/Acre"] || 0;

            if (!grouped[key]) {
                grouped[key] = {
                    key: key,
                    chemical: chem,
                    unit: unit,
                    totalDose: 0,
                    totalCalculatedDose: 0,
                    calculatedUnit: calcDoseUnit,
                    lastUsedDateStr: '',
                    lastUsedDateTime: 0,
                    blocks: {},
                    totalApplications: 0
                };
            }

            grouped[key].totalApplications += 1;

            grouped[key].totalDose += dose;
            grouped[key].totalCalculatedDose += calcDose;
            if (calcDoseUnit && !grouped[key].calculatedUnit) {
                grouped[key].calculatedUnit = calcDoseUnit;
            }

            // Track overall last used date
            const logDate = parseDate(date);
            if (logDate) {
                const t = logDate.getTime();
                if (t > grouped[key].lastUsedDateTime) {
                    grouped[key].lastUsedDateTime = t;
                    grouped[key].lastUsedDateStr = date;
                }
            }

            // Track block-specific rollup details
            if (block) {
                if (!grouped[key].blocks[block]) {
                    grouped[key].blocks[block] = {
                        block: block,
                        spraysCount: 0,
                        totalDose: 0,
                        totalCalculatedDose: 0,
                        calculatedUnit: calcDoseUnit,
                        lastUsedDateStr: '',
                        lastUsedDateTime: 0
                    };
                }
                const bData = grouped[key].blocks[block];
                bData.spraysCount += 1;
                bData.totalDose += dose;
                bData.totalCalculatedDose += calcDose;
                if (calcDoseUnit && !bData.calculatedUnit) {
                    bData.calculatedUnit = calcDoseUnit;
                }
                if (logDate) {
                    const t = logDate.getTime();
                    if (t > bData.lastUsedDateTime) {
                        bData.lastUsedDateTime = t;
                        bData.lastUsedDateStr = date;
                    }
                }
            }
        });

        // Convert blocks to sorted list inside each group
        Object.values(grouped).forEach(group => {
            group.blocksList = Object.values(group.blocks).sort((a, b) => a.block.localeCompare(b.block));
        });

        return Object.values(grouped).sort((a, b) => a.chemical.localeCompare(b.chemical));
    };

    const getFracReportsData = () => {
        const getFracCodes = (fracStr) => {
            if (!fracStr) return [];
            return fracStr.split(/[,+/]/).map(s => s.trim()).filter(Boolean);
        };

        const grouped = {};

        filteredLogs.forEach(item => {
            const block = item["Block "] || '';
            const rawFrac = item.Group || '';
            const pesticide = item.Pesticide || '';
            
            if (!block || !rawFrac) return;

            const fracs = getFracCodes(rawFrac);
            fracs.forEach(frac => {
                if (!grouped[block]) {
                    grouped[block] = {
                        block: block,
                        fracs: {}
                    };
                }
                if (!grouped[block].fracs[frac]) {
                    grouped[block].fracs[frac] = {
                        frac: frac,
                        count: 0,
                        products: new Set()
                    };
                }
                grouped[block].fracs[frac].count += 1;
                if (pesticide) {
                    grouped[block].fracs[frac].products.add(pesticide);
                }
            });
        });

        return Object.values(grouped).map(bData => {
            const fracsList = Object.values(bData.fracs).sort((a, b) => {
                const countComp = b.count - a.count;
                if (countComp !== 0) return countComp;
                return a.frac.localeCompare(b.frac);
            });
            const totalUses = fracsList.reduce((sum, f) => sum + f.count, 0);
            return {
                block: bData.block,
                fracsList: fracsList,
                totalUses: totalUses
            };
        }).sort((a, b) => a.block.localeCompare(b.block));
    };

    const toggleExpand = (key) => {
        setExpandedChems(prev => ({
            ...prev,
            [key]: !prev[key]
        }));
    };

    const toggleBlockExpand = (block) => {
        setExpandedBlocks(prev => ({
            ...prev,
            [block]: !prev[block]
        }));
    };

    const togglePhiBlockExpand = (block) => {
        setExpandedPhiBlocks(prev => ({
            ...prev,
            [block]: !prev[block]
        }));
    };

    const formatDate = (date) => {
        if (!date) return '';
        return (date.getMonth() + 1) + '/' + date.getDate() + '/' + String(date.getFullYear()).slice(-2);
    };

    const getPhiReportData = () => {
        const blockData = {};
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        // Crucial Safety Rule: We look at the ENTIRE all-time history for PHI calculations
        // so that active restrictions are never hidden by the dashboard date filter.
        history.forEach(item => {
            const block = item["Block "] || '';
            if (!block) return;

            const chem = item.Pesticide || 'Unknown Product';
            const dateStr = item.Date || '';
            const phiVal = item["PHI (d)"];
            const phiDays = (phiVal !== null && phiVal !== undefined && phiVal !== "") ? parseInt(phiVal, 10) : 0;
            
            const sprayDate = parseDate(dateStr);
            if (!sprayDate) return;

            const harvestDate = new Date(sprayDate.getTime());
            harvestDate.setDate(harvestDate.getDate() + phiDays);
            
            const tempHarvest = new Date(harvestDate.getTime());
            tempHarvest.setHours(0, 0, 0, 0);
            
            // Calculate remaining calendar days
            const diffTime = tempHarvest.getTime() - today.getTime();
            const daysRemaining = Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));

            if (!blockData[block]) {
                blockData[block] = {
                    blockCode: block,
                    status: 'Safe to Harvest',
                    earliestHarvestDate: today,
                    daysRemaining: 0,
                    limitingChem: 'None',
                    limitingDate: '',
                    limitingPhi: 0,
                    allSprays: []
                };
            }

            const sprayInfo = {
                chemical: chem,
                date: dateStr,
                phi: phiDays,
                harvestDate: tempHarvest,
                daysRemaining: daysRemaining,
                isRestricted: daysRemaining > 0
            };

            blockData[block].allSprays.push(sprayInfo);

            if (tempHarvest.getTime() > blockData[block].earliestHarvestDate.getTime()) {
                blockData[block].earliestHarvestDate = tempHarvest;
                blockData[block].daysRemaining = daysRemaining;
                blockData[block].limitingChem = chem;
                blockData[block].limitingDate = dateStr;
                blockData[block].limitingPhi = phiDays;
            }
        });

        return Object.values(blockData).map(b => {
            const isRestricted = b.daysRemaining > 0;
            b.allSprays.sort((a, b) => b.harvestDate.getTime() - a.harvestDate.getTime());
            return {
                ...b,
                status: isRestricted ? 'Restricted' : 'Safe to Harvest'
            };
        }).sort((a, b) => a.blockCode.localeCompare(b.blockCode));
    };

    const toggleReiBlockExpand = (block) => {
        setExpandedReiBlocks(prev => ({
            ...prev,
            [block]: !prev[block]
        }));
    };

    const formatDateTime = (date) => {
        if (!date) return '';
        const dStr = (date.getMonth() + 1) + '/' + date.getDate() + '/' + String(date.getFullYear()).slice(-2);
        let hours = date.getHours();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${dStr} ${hours}:${minutes} ${ampm}`;
    };

    const parseDateTime = (dateStr, timeStr) => {
        const d = parseDate(dateStr);
        if (!d) return null;
        
        let hours = 0;
        let minutes = 0;
        if (timeStr) {
            const cleanTime = String(timeStr).replace(/:/g, '').trim();
            if (cleanTime.length === 4) {
                hours = parseInt(cleanTime.slice(0, 2), 10);
                minutes = parseInt(cleanTime.slice(2, 4), 10);
            } else if (cleanTime.length === 3) {
                hours = parseInt(cleanTime.slice(0, 1), 10);
                minutes = parseInt(cleanTime.slice(1, 3), 10);
            }
        }
        
        const dt = new Date(d.getTime());
        dt.setHours(hours, minutes, 0, 0);
        return dt;
    };

    const getReiReportData = () => {
        const blockData = {};
        const now = new Date();

        // Crucial Safety Rule: We look at the ENTIRE all-time history for REI calculations
        // so that active restrictions are never hidden by the dashboard date filter.
        history.forEach(item => {
            const block = item["Block "] || '';
            if (!block) return;

            const chem = item.Pesticide || 'Unknown Product';
            const dateStr = item.Date || '';
            const timeStr = item["End Time"] || '';
            const reiVal = item["REI (h)"];
            const reiHours = (reiVal !== null && reiVal !== undefined && reiVal !== "") ? parseFloat(reiVal) : 0;
            
            const endDateTime = parseDateTime(dateStr, timeStr);
            if (!endDateTime) return;

            const safeReentryTime = new Date(endDateTime.getTime() + (reiHours * 60 * 60 * 1000));
            
            // Calculate remaining milliseconds
            const diffMs = safeReentryTime.getTime() - now.getTime();
            const isRestricted = diffMs > 0;
            const hoursRemaining = isRestricted ? Math.floor(diffMs / (1000 * 60 * 60)) : 0;
            const minutesRemaining = isRestricted ? Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60)) : 0;

            if (!blockData[block]) {
                blockData[block] = {
                    blockCode: block,
                    status: 'Safe to Enter',
                    earliestReentryTime: now,
                    hoursRemaining: 0,
                    minutesRemaining: 0,
                    limitingChem: 'None',
                    limitingDate: '',
                    limitingTime: '',
                    limitingRei: 0,
                    allSprays: []
                };
            }

            const sprayInfo = {
                chemical: chem,
                date: dateStr,
                endTime: timeStr,
                rei: reiHours,
                safeReentryTime: safeReentryTime,
                hoursRemaining: hoursRemaining,
                minutesRemaining: minutesRemaining,
                isRestricted: isRestricted
            };

            blockData[block].allSprays.push(sprayInfo);

            if (safeReentryTime.getTime() > blockData[block].earliestReentryTime.getTime()) {
                blockData[block].earliestReentryTime = safeReentryTime;
                blockData[block].hoursRemaining = hoursRemaining;
                blockData[block].minutesRemaining = minutesRemaining;
                blockData[block].limitingChem = chem;
                blockData[block].limitingDate = dateStr;
                blockData[block].limitingTime = timeStr;
                blockData[block].limitingRei = reiHours;
            }
        });

        return Object.values(blockData).map(b => {
            const isRestricted = b.earliestReentryTime.getTime() > new Date().getTime();
            b.allSprays.sort((a, b) => b.safeReentryTime.getTime() - a.safeReentryTime.getTime());
            return {
                ...b,
                status: isRestricted ? 'Restricted' : 'Safe to Enter'
            };
        }).sort((a, b) => a.blockCode.localeCompare(b.blockCode));
    };

    const reportsData = getReportsData();
    const fracReportsData = getFracReportsData();
    const phiReportData = getPhiReportData();
    const reiReportData = getReiReportData();

    // Summary stats
    const totalChemicalsUsed = new Set(filteredLogs.map(l => l.Pesticide).filter(Boolean)).size;
    const totalCampaignRuns = new Set(filteredLogs.map(l => l["Spray #"]).filter(Boolean)).size;
    const totalBlockApplications = new Set(filteredLogs.map(l => l.block_event_id).filter(Boolean)).size;

    // Years option list from actual data logs
    const getAvailableYears = () => {
        const years = new Set();
        history.forEach(item => {
            const d = parseDate(item.Date);
            if (d) years.add(d.getFullYear());
        });
        return Array.from(years).sort((a, b) => b - a);
    };

    const availableYears = getAvailableYears();

    return (
        <div className="w-100 min-vh-100 bg-light">
            <TerraNavbar />
            <Container fluid className="py-4 px-md-5">
                <div className="d-flex justify-content-between align-items-center border-bottom pb-3 mb-4">
                    <div>
                        <h1 className="text-primary m-0">Chemical Application Reports</h1>
                        <p className="text-muted m-0">Summary of chemicals and volumes sprayed</p>
                    </div>
                    <Form.Group className="d-inline-flex align-items-center">
                        <Form.Label className="me-2 mb-0 font-weight-bold text-secondary">Time Range:</Form.Label>
                        <Form.Select 
                            value={timeRange} 
                            onChange={(e) => setTimeRange(e.target.value)} 
                            style={{ width: '200px' }}
                            className="shadow-sm"
                        >
                            <option value="past-year">Past 12 Months</option>
                            <option value="all-time">All Time</option>
                            {availableYears.map(yr => (
                                <option key={yr} value={yr}>{yr} Season</option>
                            ))}
                        </Form.Select>
                    </Form.Group>
                </div>

                {loading ? (
                    <div className="text-center my-5 py-5">
                        <Spinner animation="border" variant="primary" />
                        <p className="text-muted mt-3">Loading reports data...</p>
                    </div>
                ) : (
                    <>
                        {/* Summary Widget Panel */}
                        <Row className="mb-4">
                            <Col md={4}>
                                <Card className="border-0 shadow-sm bg-primary text-white text-center py-3 w-100">
                                    <Card.Body>
                                        <Card.Title className="small uppercase text-white-50">Active Chemicals Used</Card.Title>
                                        <Card.Text className="h2 font-weight-bold">{totalChemicalsUsed}</Card.Text>
                                    </Card.Body>
                                </Card>
                            </Col>
                            <Col md={4}>
                                <Card className="border-0 shadow-sm bg-success text-white text-center py-3 w-100">
                                    <Card.Body>
                                        <Card.Title className="small uppercase text-white-50">Spray Runs (Campaigns)</Card.Title>
                                        <Card.Text className="h2 font-weight-bold">{totalCampaignRuns}</Card.Text>
                                    </Card.Body>
                                </Card>
                            </Col>
                            <Col md={4}>
                                <Card className="border-0 shadow-sm bg-info text-white text-center py-3 w-100">
                                    <Card.Body>
                                        <Card.Title className="small uppercase text-white-50">Total Block Applications</Card.Title>
                                        <Card.Text className="h2 font-weight-bold">{totalBlockApplications}</Card.Text>
                                    </Card.Body>
                                </Card>
                            </Col>
                        </Row>

                        {/* Detailed Data Table */}
                        <Card className="border-0 shadow-sm w-100">
                            <Card.Header className="bg-dark text-white py-3">
                                <h5 className="m-0">Chemical Application Aggregates</h5>
                            </Card.Header>
                            <Card.Body className="p-0">
                                {reportsData.length === 0 ? (
                                    <p className="text-muted italic p-4 text-center">No spray applications found for this time range.</p>
                                ) : (
                                    <Table hover responsive className="m-0 bg-white">
                                        <thead className="table-light">
                                            <tr>
                                                <th style={{ width: '35%' }}>Chemical Product</th>
                                                <th className="text-center" style={{ width: '15%' }}>Block Applications</th>
                                                <th className="text-center" style={{ width: '15%' }}>Last Used Date</th>
                                                <th className="text-end" style={{ width: '17%' }}>Total Dose/Acre Sprayed</th>
                                                <th className="text-end" style={{ width: '18%' }}>Total Calculated Dose</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {reportsData.map((row) => {
                                                const isExpanded = !!expandedChems[row.key];
                                                return (
                                                    <React.Fragment key={`report-group-${row.key}`}>
                                                        {/* Parent Row */}
                                                        <tr onClick={() => toggleExpand(row.key)} style={{ cursor: 'pointer' }}>
                                                            <td>
                                                                <span className="text-secondary me-2">
                                                                    {isExpanded ? '▼' : '▶'}
                                                                </span>
                                                                <strong>{row.chemical}</strong>
                                                            </td>
                                                            <td className="text-center">
                                                                <Badge bg="secondary" style={{ fontSize: '13px' }}>
                                                                    {row.totalApplications} sprays
                                                                </Badge>
                                                            </td>
                                                            <td className="text-center text-muted small">
                                                                {row.lastUsedDateStr || '-'}
                                                            </td>
                                                            <td className="text-end text-success font-weight-bold">
                                                                {row.totalDose.toFixed(2)} {row.unit}
                                                            </td>
                                                            <td className="text-end text-primary">
                                                                {row.totalCalculatedDose > 0 
                                                                    ? `${row.totalCalculatedDose.toFixed(1)} ${row.calculatedUnit}` 
                                                                    : '-'}
                                                            </td>
                                                        </tr>
                                                        {/* Accordion Detail Breakdown Row */}
                                                        {isExpanded && (
                                                            <tr>
                                                                <td colSpan={5} className="bg-light p-3">
                                                                    <div className="border rounded bg-white p-3 shadow-sm">
                                                                        <div className="d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom">
                                                                            <h6 className="m-0 text-secondary">
                                                                                Block Breakdown for <strong>{row.chemical}</strong>
                                                                            </h6>
                                                                            <Badge bg="warning" text="dark">
                                                                                Last Used: {row.lastUsedDateStr || 'N/A'}
                                                                            </Badge>
                                                                        </div>
                                                                        <Table striped bordered hover size="sm" className="m-0">
                                                                            <thead className="table-light">
                                                                                <tr>
                                                                                    <th>Block</th>
                                                                                    <th className="text-center">Sprays on Block</th>
                                                                                    <th className="text-center">Last Used in Block</th>
                                                                                    <th className="text-end">Total Dose/Ac Applied</th>
                                                                                    <th className="text-end">Total Calculated Dose</th>
                                                                                </tr>
                                                                            </thead>
                                                                            <tbody>
                                                                                {row.blocksList.map((blk, blkIdx) => (
                                                                                    <tr key={`blk-idx-${blkIdx}`}>
                                                                                        <td className="font-weight-bold text-info">{blk.block}</td>
                                                                                        <td className="text-center">
                                                                                            <Badge bg="secondary" style={{ fontSize: '12px' }}>
                                                                                                {blk.spraysCount} times
                                                                                            </Badge>
                                                                                        </td>
                                                                                        <td className="text-center text-muted small">
                                                                                            {blk.lastUsedDateStr || '-'}
                                                                                        </td>
                                                                                        <td className="text-end text-success">
                                                                                            {blk.totalDose.toFixed(2)} {row.unit}
                                                                                        </td>
                                                                                        <td className="text-end text-primary">
                                                                                            {blk.totalCalculatedDose > 0 
                                                                                                ? `${blk.totalCalculatedDose.toFixed(1)} ${blk.calculatedUnit}` 
                                                                                                : '-'}
                                                                                        </td>
                                                                                    </tr>
                                                                                ))}
                                                                            </tbody>
                                                                        </Table>
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

                        {/* FRAC Usage Table */}
                        <Card className="border-0 shadow-sm w-100 mt-4">
                            <Card.Header className="bg-dark text-white py-3">
                                <h5 className="m-0">FRAC Code Resistance Tracking (by Block)</h5>
                            </Card.Header>
                            <Card.Body className="p-0">
                                {fracReportsData.length === 0 ? (
                                    <p className="text-muted italic p-4 text-center">No chemical applications with FRAC groups found for this time range.</p>
                                ) : (
                                    <Table hover responsive className="m-0 bg-white">
                                        <thead className="table-light">
                                            <tr>
                                                <th style={{ width: '40%' }}>Block</th>
                                                <th className="text-center" style={{ width: '30%' }}>FRAC Codes Applied</th>
                                                <th className="text-center" style={{ width: '30%' }}>Total FRAC Applications</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {fracReportsData.map((row) => {
                                                const isBlockExpanded = !!expandedBlocks[row.block];
                                                return (
                                                    <React.Fragment key={`frac-block-group-${row.block}`}>
                                                        {/* Parent Block Row */}
                                                        <tr onClick={() => toggleBlockExpand(row.block)} style={{ cursor: 'pointer' }}>
                                                            <td>
                                                                <span className="text-secondary me-2">
                                                                    {isBlockExpanded ? '▼' : '▶'}
                                                                </span>
                                                                <strong className="text-info">{row.block}</strong>
                                                            </td>
                                                            <td className="text-center text-muted">
                                                                {row.fracsList.length} FRAC groups
                                                            </td>
                                                            <td className="text-center font-weight-bold text-success">
                                                                {row.totalUses} times
                                                            </td>
                                                        </tr>
                                                        {/* Accordion Detail Breakdown Row */}
                                                        {isBlockExpanded && (
                                                            <tr>
                                                                <td colSpan={3} className="bg-light p-3">
                                                                    <div className="border rounded bg-white p-3 shadow-sm">
                                                                        <div className="mb-2 pb-2 border-bottom">
                                                                            <h6 className="m-0 text-secondary">
                                                                                FRAC Code Usage details for Block <strong>{row.block}</strong>
                                                                            </h6>
                                                                        </div>
                                                                        <Table striped bordered hover size="sm" className="m-0">
                                                                            <thead className="table-light">
                                                                                <tr>
                                                                                    <th style={{ width: '30%' }}>FRAC Code</th>
                                                                                    <th className="text-center" style={{ width: '25%' }}>Times Used</th>
                                                                                    <th>Products Applied</th>
                                                                                </tr>
                                                                            </thead>
                                                                            <tbody>
                                                                                {row.fracsList.map((fRow, fIdx) => (
                                                                                    <tr key={`f-row-${fIdx}`}>
                                                                                        <td>
                                                                                            <Badge bg="warning" text="dark" style={{ fontSize: '12px', minWidth: '40px' }}>
                                                                                                Group {fRow.frac}
                                                                                            </Badge>
                                                                                        </td>
                                                                                        <td className="text-center">
                                                                                            <Badge bg="secondary">
                                                                                                {fRow.count} times
                                                                                            </Badge>
                                                                                        </td>
                                                                                        <td>
                                                                                            {Array.from(fRow.products).join(', ')}
                                                                                        </td>
                                                                                    </tr>
                                                                                ))}
                                                                            </tbody>
                                                                        </Table>
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

                        {/* Pre-Harvest Interval (PHI) Harvest Safety Report */}
                        <Card className="border-0 shadow-sm w-100 mt-4">
                            <Card.Header className="bg-dark text-white py-3">
                                <h5 className="m-0">Pre-Harvest Interval (PHI) Harvest Safety</h5>
                            </Card.Header>
                            <Card.Body className="p-0">
                                {phiReportData.length === 0 ? (
                                    <p className="text-muted italic p-4 text-center">No spray log records found to determine PHI constraints.</p>
                                ) : (
                                    <Table hover responsive className="m-0 bg-white">
                                        <thead className="table-light">
                                            <tr>
                                                <th style={{ width: '15%' }}>Block Code</th>
                                                <th className="text-center" style={{ width: '15%' }}>Harvest Status</th>
                                                <th className="text-center" style={{ width: '20%' }}>Earliest Safe Harvest Date</th>
                                                <th className="text-center" style={{ width: '15%' }}>Days Remaining</th>
                                                <th style={{ width: '35%' }}>Limiting Chemical / Constraint</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {phiReportData.map(bRow => {
                                                const isExpanded = !!expandedPhiBlocks[bRow.blockCode];
                                                const isRestricted = bRow.daysRemaining > 0;
                                                return (
                                                    <React.Fragment key={bRow.blockCode}>
                                                        <tr 
                                                            onClick={() => togglePhiBlockExpand(bRow.blockCode)}
                                                            style={{ cursor: 'pointer' }}
                                                        >
                                                            <td>
                                                                <strong className="text-primary">{bRow.blockCode.toUpperCase()}</strong>
                                                                <span className="text-muted small ms-2">
                                                                    ({isExpanded ? 'click to collapse' : 'click to expand'})
                                                                </span>
                                                            </td>
                                                            <td className="text-center">
                                                                <Badge bg={isRestricted ? "danger" : "success"}>
                                                                    {bRow.status}
                                                                </Badge>
                                                            </td>
                                                            <td className="text-center">
                                                                {isRestricted ? (
                                                                    <strong>{formatDate(bRow.earliestHarvestDate)}</strong>
                                                                ) : (
                                                                    <span className="text-success font-weight-bold">Immediately</span>
                                                                )}
                                                            </td>
                                                            <td className="text-center">
                                                                {isRestricted ? (
                                                                    <span className="text-danger font-weight-bold">{bRow.daysRemaining} days</span>
                                                                ) : (
                                                                    <span className="text-muted">0 days</span>
                                                                )}
                                                            </td>
                                                            <td>
                                                                {isRestricted ? (
                                                                    <span>
                                                                        {bRow.limitingChem} <span className="text-muted small">(sprayed on {bRow.limitingDate}, PHI: {bRow.limitingPhi}d)</span>
                                                                    </span>
                                                                ) : (
                                                                    <span className="text-muted italic">No active PHI constraints</span>
                                                                )}
                                                            </td>
                                                        </tr>
                                                        {isExpanded && (
                                                            <tr>
                                                                <td colSpan={5} className="bg-light p-3">
                                                                    <div className="border rounded shadow-sm overflow-hidden bg-white">
                                                                        <div className="bg-secondary bg-opacity-10 py-2 px-3 border-bottom">
                                                                            <span className="fw-semibold text-secondary small uppercase">
                                                                                Pesticide Applications History & PHI Status for Block {bRow.blockCode.toUpperCase()}
                                                                            </span>
                                                                        </div>
                                                                        <Table striped bordered hover size="sm" className="m-0">
                                                                            <thead className="table-light">
                                                                                <tr>
                                                                                    <th>Chemical Product</th>
                                                                                    <th className="text-center">Date Applied</th>
                                                                                    <th className="text-center">PHI (days)</th>
                                                                                    <th className="text-center">Projected Harvest Date</th>
                                                                                    <th className="text-center">Days Remaining</th>
                                                                                    <th className="text-center">Status</th>
                                                                                </tr>
                                                                            </thead>
                                                                            <tbody>
                                                                                {bRow.allSprays.map((s, idx) => (
                                                                                    <tr key={idx}>
                                                                                        <td>{s.chemical}</td>
                                                                                        <td className="text-center">{s.date}</td>
                                                                                        <td className="text-center">{s.phi} days</td>
                                                                                        <td className="text-center">{formatDate(s.harvestDate)}</td>
                                                                                        <td className="text-center">
                                                                                            {s.daysRemaining > 0 ? (
                                                                                                <span className="text-danger fw-bold">{s.daysRemaining} days</span>
                                                                                            ) : (
                                                                                                <span className="text-muted">0 days</span>
                                                                                            )}
                                                                                        </td>
                                                                                        <td className="text-center">
                                                                                            {s.daysRemaining > 0 ? (
                                                                                                <Badge bg="danger">Active</Badge>
                                                                                            ) : s.phi > 0 ? (
                                                                                                <Badge bg="secondary">Exceeded</Badge>
                                                                                            ) : (
                                                                                                <Badge bg="light" text="dark">No PHI</Badge>
                                                                                            )}
                                                                                        </td>
                                                                                    </tr>
                                                                                ))}
                                                                            </tbody>
                                                                        </Table>
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

                        {/* Restricted Entry Interval (REI) Entry Safety Report */}
                        <Card className="border-0 shadow-sm w-100 mt-4">
                            <Card.Header className="bg-dark text-white py-3">
                                <h5 className="m-0">Restricted Entry Interval (REI) Entry Safety</h5>
                            </Card.Header>
                            <Card.Body className="p-0">
                                {reiReportData.length === 0 ? (
                                    <p className="text-muted italic p-4 text-center">No spray log records found to determine REI constraints.</p>
                                ) : (
                                    <Table hover responsive className="m-0 bg-white">
                                        <thead className="table-light">
                                            <tr>
                                                <th style={{ width: '15%' }}>Block Code</th>
                                                <th className="text-center" style={{ width: '15%' }}>Entry Status</th>
                                                <th className="text-center" style={{ width: '20%' }}>Earliest Safe Entry Time</th>
                                                <th className="text-center" style={{ width: '15%' }}>Time Remaining</th>
                                                <th style={{ width: '35%' }}>Limiting Chemical / Constraint</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {reiReportData.map(bRow => {
                                                const isExpanded = !!expandedReiBlocks[bRow.blockCode];
                                                const isRestricted = bRow.status === 'Restricted';
                                                return (
                                                    <React.Fragment key={bRow.blockCode}>
                                                        <tr 
                                                            onClick={() => toggleReiBlockExpand(bRow.blockCode)}
                                                            style={{ cursor: 'pointer' }}
                                                        >
                                                            <td>
                                                                <strong className="text-primary">{bRow.blockCode.toUpperCase()}</strong>
                                                                <span className="text-muted small ms-2">
                                                                    ({isExpanded ? 'click to collapse' : 'click to expand'})
                                                                </span>
                                                            </td>
                                                            <td className="text-center">
                                                                <Badge bg={isRestricted ? "danger" : "success"}>
                                                                    {bRow.status}
                                                                </Badge>
                                                            </td>
                                                            <td className="text-center">
                                                                {isRestricted ? (
                                                                    <strong>{formatDateTime(bRow.earliestReentryTime)}</strong>
                                                                ) : (
                                                                    <span className="text-success font-weight-bold">Immediately</span>
                                                                )}
                                                            </td>
                                                            <td className="text-center">
                                                                {isRestricted ? (
                                                                    <span className="text-danger font-weight-bold">
                                                                        {bRow.hoursRemaining}h {bRow.minutesRemaining}m
                                                                    </span>
                                                                ) : (
                                                                    <span className="text-muted">0 hours</span>
                                                                )}
                                                            </td>
                                                            <td>
                                                                {isRestricted ? (
                                                                    <span>
                                                                        {bRow.limitingChem} <span className="text-muted small">(ended on {bRow.limitingDate} at {bRow.limitingTime}, REI: {bRow.limitingRei}h)</span>
                                                                    </span>
                                                                ) : (
                                                                    <span className="text-muted italic">No active REI constraints</span>
                                                                )}
                                                            </td>
                                                        </tr>
                                                        {isExpanded && (
                                                            <tr>
                                                                <td colSpan={5} className="bg-light p-3">
                                                                    <div className="border rounded shadow-sm overflow-hidden bg-white">
                                                                        <div className="bg-secondary bg-opacity-10 py-2 px-3 border-bottom">
                                                                            <span className="fw-semibold text-secondary small uppercase">
                                                                                Pesticide Applications History & REI Status for Block {bRow.blockCode.toUpperCase()}
                                                                            </span>
                                                                        </div>
                                                                        <Table striped bordered hover size="sm" className="m-0">
                                                                            <thead className="table-light">
                                                                                <tr>
                                                                                    <th>Chemical Product</th>
                                                                                    <th className="text-center">Date Applied</th>
                                                                                    <th className="text-center">End Time</th>
                                                                                    <th className="text-center">REI (hours)</th>
                                                                                    <th className="text-center">Safe Re-entry Time</th>
                                                                                    <th className="text-center">Time Remaining</th>
                                                                                    <th className="text-center">Status</th>
                                                                                </tr>
                                                                            </thead>
                                                                            <tbody>
                                                                                {bRow.allSprays.map((s, idx) => (
                                                                                    <tr key={idx}>
                                                                                        <td>{s.chemical}</td>
                                                                                        <td className="text-center">{s.date}</td>
                                                                                        <td className="text-center">{s.endTime}</td>
                                                                                        <td className="text-center">{s.rei} hours</td>
                                                                                        <td className="text-center">{formatDateTime(s.safeReentryTime)}</td>
                                                                                        <td className="text-center">
                                                                                            {s.isRestricted ? (
                                                                                                <span className="text-danger fw-bold">{s.hoursRemaining}h {s.minutesRemaining}m</span>
                                                                                            ) : (
                                                                                                <span className="text-muted">0h 0m</span>
                                                                                            )}
                                                                                        </td>
                                                                                        <td className="text-center">
                                                                                            {s.isRestricted ? (
                                                                                                <Badge bg="danger">Active</Badge>
                                                                                            ) : s.rei > 0 ? (
                                                                                                <Badge bg="secondary">Exceeded</Badge>
                                                                                            ) : (
                                                                                                <Badge bg="light" text="dark">No REI</Badge>
                                                                                            )}
                                                                                        </td>
                                                                                    </tr>
                                                                                ))}
                                                                            </tbody>
                                                                        </Table>
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
                    </>
                )}
            </Container>
        </div>
    );
}

export default SprayReports;
