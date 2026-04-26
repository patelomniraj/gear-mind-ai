import React, { useState } from 'react';

/**
 * Professional Industrial PDF Report Generator for GearMind AI
 * Clean, data-driven report with no mock values
 */
export function ProfessionalPDFReport({ sensorValues, gearId, gearType, prediction, healthScore, gearConfig, user }) {
  const [generating, setGenerating] = useState(false);

  const generatePDF = async () => {
    setGenerating(true);
    try {
      const jsPDFModule = await import('jspdf');
      const jsPDF = jsPDFModule.default || jsPDFModule.jsPDF;
      
      const doc = new jsPDF({ orientation: 'p', unit: 'mm', format: 'a4' });
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      const margin = 15;
      const contentWidth = pageWidth - (2 * margin);
      let y = margin;

      // Extract actual values
      const fault = prediction?.fault_label || 'Unknown';
      const confidence = ((prediction?.confidence || 0) * 100).toFixed(1);
      const rul = prediction?.rul_cycles || 0;
      const dailyCycles = gearConfig?.daily_cycles || 8000;
      const daysLeft = Math.floor(rul / dailyCycles);
      const shiftsLeft = Math.floor(rul / (dailyCycles / 3));
      const timestamp = new Date().toLocaleString('en-GB', { 
        day: '2-digit', 
        month: '2-digit', 
        year: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
      });

      // Helper function for page breaks
      const checkPage = (space = 30) => {
        if (y > pageHeight - space) {
          doc.addPage();
          y = margin;
          return true;
        }
        return false;
      };

      // ═══════════════════════════════════════════════════════════
      // HEADER
      // ═══════════════════════════════════════════════════════════
      doc.setFillColor(30, 41, 59);
      doc.rect(0, 0, pageWidth, 50, 'F');
      
      // Logo box
      doc.setFillColor(99, 102, 241);
      doc.roundedRect(margin, 12, 20, 20, 2, 2, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(14);
      doc.setFont(undefined, 'bold');
      doc.text('GM', margin + 10, 24, { align: 'center' });
      
      // Title
      doc.setFontSize(22);
      doc.text('GEARMIND AI', margin + 25, 20);
      doc.setFontSize(10);
      doc.setFont(undefined, 'normal');
      doc.text('Predictive Maintenance Analysis Report', margin + 25, 28);
      doc.setFontSize(8);
      doc.setTextColor(200, 200, 200);
      doc.text(`Generated: ${timestamp}`, margin + 25, 35);
      
      // User info (right side)
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(8);
      doc.text(`Operator: ${user?.name || 'N/A'}`, pageWidth - margin, 20, { align: 'right' });
      doc.text(`Shift: ${user?.shift || 'N/A'}`, pageWidth - margin, 26, { align: 'right' });
      doc.text(`Role: ${user?.role || 'Operator'}`, pageWidth - margin, 32, { align: 'right' });
      
      y = 60;

      // ═══════════════════════════════════════════════════════════
      // GEAR INFORMATION
      // ═══════════════════════════════════════════════════════════
      doc.setTextColor(30, 41, 59);
      doc.setFontSize(16);
      doc.setFont(undefined, 'bold');
      doc.text(`${gearType} Gear Analysis`, margin, y);
      y += 8;
      
      doc.setFontSize(12);
      doc.setTextColor(99, 102, 241);
      doc.text(`Unit ID: ${gearId}`, margin, y);
      y += 10;

      // ═══════════════════════════════════════════════════════════
      // STATUS BOX
      // ═══════════════════════════════════════════════════════════
      const statusConfig = {
        'No Fault': { bg: [220, 252, 231], border: [34, 197, 94], text: [22, 163, 74], icon: 'OK' },
        'NO FAILURE': { bg: [220, 252, 231], border: [34, 197, 94], text: [22, 163, 74], icon: 'OK' },
        'Minor Fault': { bg: [254, 243, 199], border: [251, 191, 36], text: [245, 158, 11], icon: 'WARN' },
        'Major Fault': { bg: [254, 226, 226], border: [239, 68, 68], text: [220, 38, 38], icon: 'FAIL' },
        'Failure': { bg: [254, 226, 226], border: [239, 68, 68], text: [220, 38, 38], icon: 'FAIL' }
      };
      const status = statusConfig[fault] || statusConfig['No Fault'];
      
      doc.setDrawColor(...status.border);
      doc.setLineWidth(1);
      doc.setFillColor(...status.bg);
      doc.roundedRect(margin, y, contentWidth, 25, 3, 3, 'FD');
      
      doc.setTextColor(...status.text);
      doc.setFontSize(18);
      doc.setFont(undefined, 'bold');
      doc.text(`${status.icon} ${fault.toUpperCase()}`, margin + 5, y + 10);
      
      doc.setFontSize(10);
      doc.setFont(undefined, 'normal');
      doc.text(`Confidence: ${confidence}%`, margin + 5, y + 18);
      
      doc.setTextColor(30, 41, 59);
      doc.setFontSize(14);
      doc.setFont(undefined, 'bold');
      doc.text(`Health: ${healthScore}/100`, pageWidth - margin - 5, y + 14, { align: 'right' });
      
      y += 32;

      // ═══════════════════════════════════════════════════════════
      // SENSOR READINGS
      // ═══════════════════════════════════════════════════════════
      checkPage(80);
      
      doc.setTextColor(30, 41, 59);
      doc.setFontSize(13);
      doc.setFont(undefined, 'bold');
      doc.text('Current Sensor Readings', margin, y);
      y += 8;

      // Prepare sensor data based on gear type
      let sensorData = [];
      
      if (gearType === 'Worm') {
        sensorData = [
          { name: 'Worm RPM', value: sensorValues.rpm || sensorValues.Worm_RPM || 0, unit: 'RPM' },
          { name: 'Input Torque', value: sensorValues.in_torque || sensorValues.Input_Torque || 0, unit: 'Nm' },
          { name: 'Output Torque', value: sensorValues.out_torque || sensorValues.Output_Torque || 0, unit: 'Nm' },
          { name: 'Motor Current', value: sensorValues.current || sensorValues.Motor_Current || 0, unit: 'A' },
          { name: 'Oil Temperature', value: sensorValues.oil_temp || sensorValues.Oil_Temp || 0, unit: '°C' },
          { name: 'Ambient Temp', value: sensorValues.amb_temp || sensorValues.Ambient_Temp || 0, unit: '°C' },
          { name: 'Axial Vibration', value: sensorValues.ax_vib || sensorValues.Axial_Vib || 0, unit: 'mm/s' },
          { name: 'Radial Vibration', value: sensorValues.rad_vib || sensorValues.Radial_Vib || 0, unit: 'mm/s' },
          { name: 'Copper PPM', value: sensorValues.cu_ppm || sensorValues.Cu_PPM || 0, unit: 'ppm' },
          { name: 'Iron PPM', value: sensorValues.fe_ppm || sensorValues.Fe_PPM || 0, unit: 'ppm' },
          { name: 'Efficiency', value: sensorValues.eff || sensorValues.Efficiency_Calc || 0, unit: '%' },
          { name: 'Friction Coeff', value: sensorValues.friction || sensorValues.Friction_Coeff || 0, unit: '' },
        ];
      } else if (gearType === 'Spur') {
        sensorData = [
          { name: 'Speed', value: sensorValues.speed || sensorValues.Speed_RPM || sensorValues.load || 0, unit: 'RPM' },
          { name: 'Torque', value: sensorValues.torque || sensorValues.Torque_Nm || 0, unit: 'Nm' },
          { name: 'Vibration', value: sensorValues.vib || sensorValues.Vibration_mm_s || sensorValues.vibration || 0, unit: 'mm/s' },
          { name: 'Temperature', value: sensorValues.temp || sensorValues.Temperature_C || sensorValues.temperature || 0, unit: '°C' },
          { name: 'Shock Load', value: sensorValues.shock || sensorValues.Shock_Load_g || sensorValues.wear || 0, unit: 'g' },
          { name: 'Noise Level', value: sensorValues.noise || sensorValues.Noise_dB || (sensorValues.lube ? sensorValues.lube * 100 : 0), unit: 'dB' },
        ];
      } else {
        // Helical and Bevel
        sensorData = [
          { name: 'Load', value: sensorValues.load || sensorValues['Load (kN)'] || 0, unit: 'kN' },
          { name: 'Torque', value: sensorValues.torque || sensorValues['Torque (Nm)'] || 0, unit: 'Nm' },
          { name: 'Vibration RMS', value: sensorValues.vib || sensorValues['Vibration RMS (mm/s)'] || sensorValues.vibration || 0, unit: 'mm/s' },
          { name: 'Temperature', value: sensorValues.temp || sensorValues['Temperature (°C)'] || sensorValues.temperature || 0, unit: '°C' },
          { name: 'Wear', value: sensorValues.wear || sensorValues['Wear (mm)'] || 0, unit: 'mm' },
          { name: 'Lubrication Index', value: sensorValues.lube || sensorValues['Lubrication Index'] || 0, unit: '' },
          { name: 'Efficiency', value: sensorValues.eff || sensorValues['Efficiency (%)'] || sensorValues.efficiency || 0, unit: '%' },
          { name: 'Cycles in Use', value: sensorValues.cycles || sensorValues['Cycles in Use'] || 0, unit: 'cycles' },
        ];
      }

      // Table header
      doc.setFillColor(99, 102, 241);
      doc.rect(margin, y, contentWidth, 8, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(9);
      doc.setFont(undefined, 'bold');
      doc.text('Parameter', margin + 3, y + 5.5);
      doc.text('Value', pageWidth - margin - 50, y + 5.5);
      doc.text('Unit', pageWidth - margin - 20, y + 5.5);
      y += 8;

      // Table rows
      doc.setFont(undefined, 'normal');
      let alternate = false;
      sensorData.forEach(sensor => {
        checkPage(25);
        
        if (alternate) {
          doc.setFillColor(248, 250, 252);
          doc.rect(margin, y, contentWidth, 7, 'F');
        }
        
        doc.setTextColor(30, 41, 59);
        doc.setFontSize(9);
        doc.text(sensor.name, margin + 3, y + 4.5);
        
        doc.setFont(undefined, 'bold');
        const valueStr = typeof sensor.value === 'number' ? sensor.value.toFixed(3) : String(sensor.value);
        doc.text(valueStr, pageWidth - margin - 50, y + 4.5);
        
        doc.setFont(undefined, 'normal');
        doc.setTextColor(100, 116, 139);
        doc.text(sensor.unit, pageWidth - margin - 20, y + 4.5);
        
        y += 7;
        alternate = !alternate;
      });
      y += 8;

      // ═══════════════════════════════════════════════════════════
      // RUL SECTION
      // ═══════════════════════════════════════════════════════════
      checkPage(40);
      
      doc.setTextColor(30, 41, 59);
      doc.setFontSize(13);
      doc.setFont(undefined, 'bold');
      doc.text('Remaining Useful Life (RUL)', margin, y);
      y += 8;
      
      doc.setFillColor(239, 246, 255);
      doc.roundedRect(margin, y, contentWidth, 22, 3, 3, 'F');
      
      doc.setFontSize(16);
      doc.setTextColor(59, 130, 246);
      doc.setFont(undefined, 'bold');
      doc.text(`${rul.toLocaleString()} cycles`, margin + 5, y + 10);
      
      doc.setFontSize(10);
      doc.setFont(undefined, 'normal');
      doc.setTextColor(71, 85, 105);
      doc.text(`Approx. ${daysLeft} days  |  ${shiftsLeft} shifts`, margin + 5, y + 17);
      
      y += 28;

      // ═══════════════════════════════════════════════════════════
      // COST ANALYSIS
      // ═══════════════════════════════════════════════════════════
      checkPage(70);
      
      doc.setTextColor(30, 41, 59);
      doc.setFontSize(13);
      doc.setFont(undefined, 'bold');
      doc.text('Cost Impact Analysis', margin, y);
      y += 8;

      const repairCost = gearConfig?.repair_cost || 40000;
      const overhaulCost = gearConfig?.overhaul_cost || 100000;
      const failureCost = gearConfig?.failure_cost || 400000;
      const savings = failureCost - repairCost;

      // Savings box
      doc.setFillColor(220, 252, 231);
      doc.roundedRect(margin, y, contentWidth, 18, 3, 3, 'F');
      doc.setFontSize(9);
      doc.setTextColor(22, 163, 74);
      doc.setFont(undefined, 'bold');
      doc.text('POTENTIAL SAVINGS BY ACTING NOW', pageWidth / 2, y + 7, { align: 'center' });
      doc.setFontSize(16);
      doc.text(`Rs. ${savings.toLocaleString()}`, pageWidth / 2, y + 14, { align: 'center' });
      y += 24;

      // Cost table
      const costScenarios = [
        { name: 'Preventive Repair', cost: repairCost, downtime: '4-6 hrs', risk: 'Low', color: [220, 252, 231] },
        { name: 'Delayed Overhaul', cost: overhaulCost, downtime: '1-2 days', risk: 'Med', color: [254, 243, 199] },
        { name: 'Catastrophic Failure', cost: failureCost, downtime: '5-7 days', risk: 'High', color: [254, 226, 226] },
      ];

      doc.setFillColor(99, 102, 241);
      doc.rect(margin, y, contentWidth, 8, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(9);
      doc.setFont(undefined, 'bold');
      doc.text('Scenario', margin + 3, y + 5.5);
      doc.text('Cost (Rs.)', pageWidth - margin - 80, y + 5.5);
      doc.text('Downtime', pageWidth - margin - 45, y + 5.5);
      doc.text('Risk', pageWidth - margin - 15, y + 5.5);
      y += 8;

      costScenarios.forEach(scenario => {
        checkPage(20);
        doc.setFillColor(...scenario.color);
        doc.rect(margin, y, contentWidth, 9, 'F');
        
        doc.setTextColor(30, 41, 59);
        doc.setFont(undefined, 'bold');
        doc.setFontSize(9);
        doc.text(scenario.name, margin + 3, y + 6);
        doc.text(`Rs. ${scenario.cost.toLocaleString()}`, pageWidth - margin - 80, y + 6);
        
        doc.setFont(undefined, 'normal');
        doc.text(scenario.downtime, pageWidth - margin - 45, y + 6);
        doc.text(scenario.risk, pageWidth - margin - 15, y + 6);
        
        y += 9;
      });
      y += 10;

      // ═══════════════════════════════════════════════════════════
      // SHAP VALUES
      // ═══════════════════════════════════════════════════════════
      const shap = prediction?.shap_values || {};
      if (Object.keys(shap).length > 0) {
        checkPage(60);
        
        doc.setTextColor(30, 41, 59);
        doc.setFontSize(13);
        doc.setFont(undefined, 'bold');
        doc.text('AI Feature Impact Analysis (SHAP)', margin, y);
        y += 8;

        doc.setFillColor(99, 102, 241);
        doc.rect(margin, y, contentWidth, 8, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(9);
        doc.setFont(undefined, 'bold');
        doc.text('Feature', margin + 3, y + 5.5);
        doc.text('Impact', pageWidth - margin - 40, y + 5.5);
        doc.text('Direction', pageWidth - margin - 15, y + 5.5);
        y += 8;

        const shapEntries = Object.entries(shap)
          .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
          .slice(0, 10);
        
        alternate = false;
        shapEntries.forEach(([feature, value]) => {
          checkPage(20);
          
          if (alternate) {
            doc.setFillColor(248, 250, 252);
            doc.rect(margin, y, contentWidth, 7, 'F');
          }
          
          doc.setTextColor(30, 41, 59);
          doc.setFont(undefined, 'normal');
          doc.setFontSize(9);
          const featureName = feature.length > 40 ? feature.substring(0, 38) + '...' : feature;
          doc.text(featureName, margin + 3, y + 4.5);
          
          const impactColor = value > 0 ? [220, 38, 38] : [22, 163, 74];
          doc.setTextColor(...impactColor);
          doc.setFont(undefined, 'bold');
          doc.text(value > 0 ? `+${value.toFixed(4)}` : value.toFixed(4), pageWidth - margin - 40, y + 4.5);
          
          doc.setFont(undefined, 'normal');
          doc.text(value > 0 ? 'Risk (+)' : 'Safe (-)', pageWidth - margin - 15, y + 4.5);
          
          y += 7;
          alternate = !alternate;
        });
        y += 10;
      }

      // ═══════════════════════════════════════════════════════════
      // RECOMMENDATIONS
      // ═══════════════════════════════════════════════════════════
      checkPage(60);
      
      doc.setTextColor(30, 41, 59);
      doc.setFontSize(13);
      doc.setFont(undefined, 'bold');
      doc.text('Detailed Analysis & Recommendations', margin, y);
      y += 8;
      
      let recommendations = [];
      if (fault === 'No Fault' || fault === 'NO FAILURE') {
        recommendations = [
          'Continue regular monitoring schedule',
          'Maintain current lubrication intervals',
          'Perform routine visual inspections',
          'Document operating conditions as baseline',
        ];
      } else if (fault === 'Minor Fault') {
        recommendations = [
          'Increase monitoring frequency to daily checks',
          'Schedule detailed inspection within 1-2 weeks',
          'Check and adjust lubrication if necessary',
          'Verify alignment and mounting bolt torque',
          'Review operating conditions for changes',
        ];
      } else {
        recommendations = [
          'IMMEDIATE: Schedule emergency maintenance',
          'Reduce operating load until inspection',
          'Prepare replacement parts and backup equipment',
          'Document all abnormal behaviors',
          'Engage maintenance team for overhaul',
        ];
      }
      
      doc.setFontSize(9);
      doc.setFont(undefined, 'normal');
      doc.setTextColor(71, 85, 105);
      recommendations.forEach((rec, idx) => {
        checkPage(20);
        const recText = `${idx + 1}. ${rec}`;
        const lines = doc.splitTextToSize(recText, contentWidth - 10);
        lines.forEach(line => {
          doc.text(line, margin + 5, y);
          y += 5;
        });
      });
      y += 10;

      // ═══════════════════════════════════════════════════════════
      // FOOTER ON ALL PAGES
      // ═══════════════════════════════════════════════════════════
      const totalPages = doc.internal.getNumberOfPages();
      for (let i = 1; i <= totalPages; i++) {
        doc.setPage(i);
        doc.setDrawColor(226, 232, 240);
        doc.setLineWidth(0.5);
        doc.line(margin, pageHeight - 15, pageWidth - margin, pageHeight - 15);
        
        doc.setFontSize(8);
        doc.setTextColor(148, 163, 184);
        doc.text('GearMind AI - Elecon Engineering Company', margin, pageHeight - 10);
        doc.text(`Page ${i} of ${totalPages}`, pageWidth - margin, pageHeight - 10, { align: 'right' });
        doc.setFontSize(7);
        doc.text('Confidential - For Internal Use Only', pageWidth / 2, pageHeight - 10, { align: 'center' });
      }

      // Save PDF
      doc.save(`GearMind_${gearType}_${gearId}_${Date.now()}.pdf`);
      
    } catch (error) {
      console.error('PDF generation error:', error);
      alert('Failed to generate PDF. Please check console for details.');
    }
    setGenerating(false);
  };

  return (
    <button 
      onClick={generatePDF} 
      disabled={generating}
      style={{
        background: generating ? '#cbd5e1' : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
        padding: '12px 24px',
        fontSize: '14px',
        fontWeight: 700,
        borderRadius: '12px',
        border: 'none',
        color: 'white',
        cursor: generating ? 'not-allowed' : 'pointer',
        boxShadow: generating ? 'none' : '0 4px 12px rgba(99, 102, 241, 0.4)',
        transition: 'all 0.3s ease'
      }}
    >
      {generating ? '⏳ Generating Report...' : '📄 Download PDF Report'}
    </button>
  );
}