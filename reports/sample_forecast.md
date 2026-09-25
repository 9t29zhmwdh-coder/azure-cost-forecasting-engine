# Azure Cost Forecasting Report
**Generated:** 2026-09-25  
**Subscription:** `demo-subscription`  
**History:** 90 days  
**Currency:** USD
---

## Historical Summary
| Metric | Value |
|---|---|
| Average daily cost | 2098.68 |
| Total cost (90d) | 188881.52 |
---

## Cost Forecast
| Horizon | Projected Total | vs. Baseline | Trend |
|---|---|---|---|
| 30 days | 70831.65 | +1228.45 | stable (+0.248%/day) |
| 60 days | 144585.46 | +5379.05 | stable (+0.248%/day) |
| 90 days | 221261.42 | +12451.81 | stable (+0.248%/day) |
---

## Anomalies
| Date | Cost | z-score |
|---|---|---|
| 2026-08-28 | 5504.28 | 8.7 |

---

## Trends by Service and Resource Group
| Type | Name | Trend | Change per day | Avg daily cost |
|---|---|---|---|---|
| Service | Microsoft.Compute | increasing | +0.38% | 1405.47 |
| Resource group | rg-app | increasing | +0.37% | 1586.65 |
| Service | Microsoft.Web | increasing | +0.31% | 181.17 |
| Service | Microsoft.Monitor | stable | +0.01% | 45.88 |
| Service | Microsoft.KeyVault | stable | +0.00% | 5.19 |
| Service | Microsoft.Sql | stable | -0.01% | 342.49 |
| Resource group | rg-data | stable | -0.01% | 430.51 |
| Service | Microsoft.Storage | stable | -0.05% | 88.02 |
| Resource group | rg-shared | stable | -0.10% | 81.53 |
| Service | Microsoft.Network | stable | -0.29% | 30.46 |

---

## Cost Optimization Recommendations
**Total estimated monthly saving: 8132.66**

| Severity | Category | Service | Est. Monthly Saving | Description |
|---|---|---|---|---|
| 🔴 HIGH | reserved_instance | Microsoft.Sql | 3596.09 (35%) | Reserved Instance candidate: Microsoft.Sql |
| 🔴 HIGH | reserved_instance | Microsoft.Web | 1902.33 (35%) | Reserved Instance candidate: Microsoft.Web |
| 🔴 HIGH | anomaly | Microsoft.Compute | 1133.24 (242%) | Cost spike detected: Microsoft.Compute |
| 🔴 HIGH | reserved_instance | Microsoft.Storage | 924.26 (35%) | Reserved Instance candidate: Microsoft.Storage |
| 🔴 HIGH | reserved_instance | Microsoft.Monitor | 481.75 (35%) | Reserved Instance candidate: Microsoft.Monitor |
| 🟡 MEDIUM | rightsizing | Microsoft.Compute | 48.10 (30%) | Growing cost: Microsoft.Compute |
| 🔴 HIGH | anomaly | Microsoft.Web | 18.94 (31%) | Cost spike detected: Microsoft.Web |
| 🔴 HIGH | anomaly | Microsoft.Network | 18.50 (182%) | Cost spike detected: Microsoft.Network |
| 🟡 MEDIUM | rightsizing | Microsoft.Web | 5.02 (30%) | Growing cost: Microsoft.Web |
| 🟡 MEDIUM | anomaly | Microsoft.Storage | 4.43 (15%) | Cost spike detected: Microsoft.Storage |

### 1. Reserved Instance candidate: Microsoft.Sql

Microsoft.Sql shows highly predictable usage (coefficient of variation 1.9%) over 90 days. A 1-year Reserved Instance or Savings Plan commitment could reduce this cost by approximately 35%.

**Estimated monthly saving:** 3596.09 (35%)  
**Severity:** HIGH  
**Category:** reserved_instance

### 2. Reserved Instance candidate: Microsoft.Web

Microsoft.Web shows highly predictable usage (coefficient of variation 10.8%) over 90 days. A 1-year Reserved Instance or Savings Plan commitment could reduce this cost by approximately 35%.

**Estimated monthly saving:** 1902.33 (35%)  
**Severity:** HIGH  
**Category:** reserved_instance

### 3. Cost spike detected: Microsoft.Compute

Microsoft.Compute had 1 cost spike(s) exceeding mean + 2.5 standard deviations (latest: 2026-08-28). Average spike excess: 3399.71 per day. Investigate for runaway workloads, misconfigured autoscaling, or unexpected data transfer events.

**Estimated monthly saving:** 1133.24 (242%)  
**Severity:** HIGH  
**Category:** anomaly

### 4. Reserved Instance candidate: Microsoft.Storage

Microsoft.Storage shows highly predictable usage (coefficient of variation 4.7%) over 90 days. A 1-year Reserved Instance or Savings Plan commitment could reduce this cost by approximately 35%.

**Estimated monthly saving:** 924.26 (35%)  
**Severity:** HIGH  
**Category:** reserved_instance

### 5. Reserved Instance candidate: Microsoft.Monitor

Microsoft.Monitor shows highly predictable usage (coefficient of variation 6.4%) over 90 days. A 1-year Reserved Instance or Savings Plan commitment could reduce this cost by approximately 35%.

**Estimated monthly saving:** 481.75 (35%)  
**Severity:** HIGH  
**Category:** reserved_instance

### 6. Growing cost: Microsoft.Compute

Microsoft.Compute is growing at 0.4% of its average daily cost per day. Without intervention this will add approximately 160 per month. Review resource scaling policies, autoscaling upper limits, and provisioned capacity that is not actively consumed.

**Estimated monthly saving:** 48.10 (30%)  
**Severity:** MEDIUM  
**Category:** rightsizing

### 7. Cost spike detected: Microsoft.Web

Microsoft.Web had 1 cost spike(s) exceeding mean + 2.5 standard deviations (latest: 2026-09-20). Average spike excess: 56.81 per day. Investigate for runaway workloads, misconfigured autoscaling, or unexpected data transfer events.

**Estimated monthly saving:** 18.94 (31%)  
**Severity:** HIGH  
**Category:** anomaly

### 8. Cost spike detected: Microsoft.Network

Microsoft.Network had 1 cost spike(s) exceeding mean + 2.5 standard deviations (latest: 2026-07-27). Average spike excess: 55.51 per day. Investigate for runaway workloads, misconfigured autoscaling, or unexpected data transfer events.

**Estimated monthly saving:** 18.50 (182%)  
**Severity:** HIGH  
**Category:** anomaly

### 9. Growing cost: Microsoft.Web

Microsoft.Web is growing at 0.3% of its average daily cost per day. Without intervention this will add approximately 17 per month. Review resource scaling policies, autoscaling upper limits, and provisioned capacity that is not actively consumed.

**Estimated monthly saving:** 5.02 (30%)  
**Severity:** MEDIUM  
**Category:** rightsizing

### 10. Cost spike detected: Microsoft.Storage

Microsoft.Storage had 1 cost spike(s) exceeding mean + 2.5 standard deviations (latest: 2026-08-02). Average spike excess: 13.30 per day. Investigate for runaway workloads, misconfigured autoscaling, or unexpected data transfer events.

**Estimated monthly saving:** 4.43 (15%)  
**Severity:** MEDIUM  
**Category:** anomaly

---

*Generated by Azure Cost Forecasting Engine. RayStudio*
