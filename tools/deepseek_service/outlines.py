# --- Provincial outline -------------------------------------------------
provincial_company_outline = [
    {
        "id": 1,
        "parentID": None,
        "title": "Network Scale Analysis",
        "level": "1",
        "content": "",
        "principle": "Count CT/CU 4G/5G base stations and sharing ratio; distinguish macro, indoor (DAS), and low-band structures; tabulate inter-city differences.",
        "info_needed": [
            {"Number of gNBs": "gnbNums"},
            {"Number of site-sets": "setGnbNums"},
            {"RRU/AAU count": "rruNums"},
            {"Shared site-sets": "shareSetGnbNums"},
            {"Share of site-sets": "shareSetGnbRate"},
            {"Low-band site scale": "fill manually"}
        ],
        "methods": "ranking, share calculation"
    },
    {
        "id": 2,
        "parentID": 1,
        "title": "4G Sharing Depth",
        "level": "2",
        "content": "",
        "principle": "Focus on mid/low-band sharing ratio differences; highlight CT→CU vs CU→CT asymmetry.",
        "info_needed": [
            {"Total 4G cells": "cellNums"},
            {"Shared cells (enabled)": "shareCellNums"},
            {"Sharing ratio": "shareCellRate"}
        ],
        "methods": "MoM, variance analysis"
    },
    {
        "id": 3,
        "parentID": 1,
        "title": "5G Layered Carrying",
        "level": "2",
        "content": "",
        "principle": "Compare 3.5 GHz/2.1 GHz site density; relate 40 MHz activation progress below county level with traffic uplift.",
        "info_needed": [
            {"Total cells – SA": "cellSaNums"},
            {"RRU/AAU count – TOC": "rru2cNums"},
            {"5G daily avg total traffic (TB)": "flux5g7avg"}
        ],
        "methods": "correlation analysis"
    },
    {
        "id": 4,
        "parentID": None,
        "title": "Spectrum Efficiency Assessment",
        "level": "1",
        "content": "",
        "principle": "Evaluate 40 MHz bandwidth impact on PRB utilization and user rates; separate urban vs rural scenarios.",
        "info_needed": [
            {"5G DL PRB avg utilization": "prbUseddlRate"},
            {"5G user DL avg throughput": "userKpiRateTelDl"},
            {"4G DL avg PRB utilization": "puschprbtotmeandlRate"}
        ],
        "methods": "YoY, variance analysis"
    },
    {
        "id": 5,
        "parentID": 4,
        "title": "Interference Control Effectiveness",
        "level": "2",
        "content": "",
        "principle": "Compare SINR degradation for spatial isolation vs physical isolation scenarios.",
        "info_needed": [
            {"5G CQI good rate": "cqiGoodRatio"},
            {"4G CQI good ratio": "cqiGoodrate"}
        ],
        "methods": "variance analysis"
    },
    {
        "id": 6,
        "parentID": None,
        "title": "Frequency Clearing Implementation",
        "level": "1",
        "content": "",
        "principle": "Count equipment replacements and investment; describe use of transfer-to-direct modules in indoor DAS retrofits.",
        "info_needed": [
            {"RRU count": "rruNums"},
            {"PRRU count": "prruNums"},
            {"Equipment replacement investment": "fill manually"}
        ],
        "methods": "ranking, share calculation"
    },
    {
        "id": 7,
        "parentID": 6,
        "title": "Load Offloading Strategy",
        "level": "2",
        "content": "",
        "principle": "Plan release based on combined PRB utilization thresholds; relate to enabling 1.8 GHz dual carriers.",
        "info_needed": [
            {"4G UL PRB utilization": "puschprbtotmeanulRate"},
            {"4G DL PRB utilization": "puschprbtotmeandlRate"}
        ],
        "methods": "correlation analysis"
    },
    {
        "id": 8,
        "parentID": None,
        "title": "Urban–Rural Gap Management",
        "level": "1",
        "content": "",
        "principle": "Compare traffic absorption efficiency: contiguous county openings vs patchwork urban deployments.",
        "info_needed": [
            {"5G traffic residence ratio": "loginUserTrafficRemainRate"},
            {"4/5G total traffic": "fourFifthTraffic"}
        ],
        "methods": "MoM, ranking"
    },
    {
        "id": 9,
        "parentID": 8,
        "title": "Indoor DAS Retrofit Bottlenecks",
        "level": "2",
        "content": "",
        "principle": "Compare techno-economics of digital DAS re-frequency vs traditional DAS replacement.",
        "info_needed": [
            {"PRRU count": "prruNums"},
            {"Equipment replacement cost": "fill manually"}
        ],
        "methods": "variance analysis"
    },
    {
        "id": 10,
        "parentID": None,
        "title": "Dynamic Optimization Mechanism",
        "level": "1",
        "content": "",
        "principle": "Build a 3D model (load–offload ratio–terminal penetration) to output expansion thresholds.",
        "info_needed": [
            {"5G offload ratio": "fifthTrafficShuntRate"},
            {"5G terminal attach rate": "loginUserRate"}
        ],
        "methods": "correlation analysis"
    }
]

# --- Metrics dictionary (EN) -------------------------------------------------
data = {
  "Total cells": "Count of cells.",
  "Number of base stations": "Count of base stations.",
  "Number of site-sets": "Estimated site-sets: indoor RRU/AAU ÷ 2.5, outdoor RRU/AAU ÷ 3, PRRU ÷ 24.",
  "RRU/AAU count": "Count of RRUs or AAUs.",
  "PRRU count": "Count of PRRUs.",
  "Total equipment count": "Count of all equipment.",
  "Total cells – TOC": "Cell count with coverage type = TOC.",
  "Total cells – TOB": "Cell count with coverage type = TOB.",
  "Total cells – TOB&TOC": "Cell count with coverage type = TOB&TOC.",
  "Total cells – NSA": "Cell count in NSA.",
  "Total cells – SA": "Cell count in SA.",
  "Total cells – NSA&SA": "Cells having both NSA and SA.",
  "Site-sets – TOC": "Estimated site-sets for TOC devices.",
  "Site-sets – TOB": "Estimated site-sets for TOB devices.",
  "Site-sets – TOB&TOC": "Estimated site-sets for TOB&TOC devices.",
  "RRU/AAU count – TOC": "RRU/AAU count for TOC.",
  "RRU/AAU count – TOB": "RRU/AAU count for TOB.",
  "RRU/AAU count – TOB&TOC": "RRU/AAU count for TOB&TOC.",
  "PRRU count – TOC": "PRRU count for TOC.",
  "PRRU count – TOB": "PRRU count for TOB.",
  "PRRU count – TOB&TOC": "PRRU count for TOB&TOC.",
  "Equipment count – TOC": "All equipment count for TOC.",
  "Equipment count – TOB": "All equipment count for TOB.",
  "Equipment count – TOB&TOC": "All equipment count for TOB&TOC.",
  "Site-sets – 2CC&3CC (≥200M)": "Estimated site-sets with multi-carrier (≥200 MHz).",
  "RRU/AAU count – 2CC&3CC (≥200M)": "RRU/AAU count with multi-carrier (≥200 MHz).",
  "PRRU count – 2CC&3CC (≥200M)": "PRRU count with multi-carrier (≥200 MHz).",
  "Equipment count – 2CC&3CC (≥200M)": "All equipment count with multi-carrier (≥200 MHz).",
  "Site-sets – 2CC (200M)": "Estimated site-sets with 2CC (200 MHz).",
  "RRU/AAU count – 2CC (200M)": "RRU/AAU count with 2CC (200 MHz).",
  "PRRU count – 2CC (200M)": "PRRU count with 2CC (200 MHz).",
  "Equipment count – 2CC (200M)": "All equipment count with 2CC (200 MHz).",
  "Site-sets – 3CC (300M)": "Estimated site-sets with 3CC (300 MHz).",
  "RRU/AAU count – 3CC (300M)": "RRU/AAU count with 3CC (300 MHz).",
  "PRRU count – 3CC (300M)": "PRRU count with 3CC (300 MHz).",
  "Equipment count – 3CC (300M)": "All equipment count with 3CC (300 MHz).",
  "Total cells – dual-mode": "Cells with both 4G and 5G enabled.",
  "Site-sets – dual-mode": "Estimated site-sets for dual-mode equipment.",
  "RRU/AAU count – dual-mode": "RRU/AAU count with both 4G and 5G.",
  "PRRU count – dual-mode": "PRRU count with both 4G and 5G.",
  "Equipment count – dual-mode": "All equipment with both 4G and 5G.",
  "Cells with perception inequality": "Count where user-perceived KPIs between CT/CU are unequal (composite).",
  "Cells with user-service mismatch": "(CU traffic share − CU user share) absolute > 0.2 and daily CT+CU RRC users > 5.",
  "CU one-sided zero-traffic cells": "CT users = 0, CU users > 0.",
  "CT one-sided zero-traffic cells": "CU users = 0, CT users > 0.",
  "Cells with unequal per-user rate": "Abs((CU 4G DL rate − CT 4G DL rate) / max(CT,CU per-user DL rate)) > 0.5 AND CT+CU daily traffic > 250 MB AND max per-user DL rate > 5 Mbps.",
  "Cells with unequal call setup rate": "Abs(CU E-RAB setup success − CT E-RAB setup success) > 0.02 AND total RRC requests > 100/day.",
  "Cells with unequal drop rate": "Abs(CU E-RAB drop − CT E-RAB drop) > 0.01 AND total drops > 10/day.",
  "Cells with unequal HO success rate": "Abs(CU intra-4G HO success − CT intra-4G HO success) > 0.02 AND total HO failures > 100/day.",
  "5G traffic (B-domain)": "5G traffic produced by 5G terminal users.",
  "4G traffic (B-domain)": "4G network traffic.",
  "4/5G total traffic (B-domain)": "5G traffic by 5G terminals + 4G network traffic.",
  "5G offload ratio (B-domain)": "5G traffic / (5G traffic + 4G traffic).",
  "Number of shared cells": "Count of cells with sharing flag = yes.",
  "Share of shared cells": "Shared cells / total cells.",
  "Shared site-sets (estimated)": "For shared cells: PRRU÷24, indoor RRU÷2.5, outdoor RRU÷3 (estimated site-sets).",
  "Share of site-sets (shared)": "Estimated shared site-sets / estimated total site-sets.",
  "5G terminal users (10k) (B-domain)": "Number of 5G terminal users.",
  "5G attached users (10k) (B-domain)": "5G terminals attached to network.",
  "5G terminal attach rate (B-domain)": "Attached 5G terminals / total 5G terminal users.",
  "Attached users total traffic (B-domain)": "5G traffic by 5G terminals + 4G traffic by 5G terminals.",
  "5G traffic residence ratio (B-domain)": "5G traffic by 5G terminals / (5G traffic + 4G traffic by 5G terminals).",
  "RSRP total samples": "Total MR samples.",
  "RSRP ≥ −110 samples": "MR samples with signal strength ≥ −110 dBm.",
  "RSRP ≥ −110 share": "Share of MR samples with RSRP ≥ −110 dBm.",
  "4G total traffic (TB)": "Sum of PDCP UL+DL during the period.",
  "4G total traffic (TB) – CT": "Sum of PDCP UL+DL for CT users.",
  "4G total traffic (TB) – CU": "Sum of PDCP UL+DL for CU users.",
  "4G daily avg total traffic (TB)": "Average PDCP UL+DL during the period.",
  "4G daily avg total traffic (TB) – CT": "Average PDCP UL+DL for CT users.",
  "4G daily avg total traffic (TB) – CU": "Average PDCP UL+DL for CU users.",
  "4G UL avg occupied PRBs": "Avg number of occupied UL PRBs.",
  "4G UL available PRBs": "Number of available UL PRBs.",
  "4G UL avg PRB utilization (%)": "Avg occupied UL PRBs / available UL PRBs.",
  "4G DL avg occupied PRBs": "Avg number of occupied DL PRBs.",
  "4G DL available PRBs": "Number of available DL PRBs.",
  "4G DL avg PRB utilization (%)": "Avg occupied DL PRBs / available DL PRBs.",
  "4G avg RRC connected users": "Sum of avg RRC connected users during the period.",
  "4G RRC setup successes": "Sum of RRC connection setup successes.",
  "4G RRC setup requests": "Sum of RRC connection setup requests.",
  "4G RRC setup success rate": "RRC setup successes / requests.",
  "4G E-RAB setup successes": "Sum of E-RAB setup successes.",
  "4G E-RAB setup requests": "Sum of E-RAB setup requests.",
  "4G radio access success rate": "RRC setup success × E-RAB setup success.",
  "4G E-RAB abnormal releases": "Sum of abnormal E-RAB releases.",
  "4G E-RAB normal releases": "Sum of normal E-RAB releases.",
  "4G E-RAB drop rate": "Abnormal releases / (abnormal + normal releases).",
  "4G X2 HO successes": "Sum of X2 HO successes.",
  "4G X2 HO requests": "Sum of X2 HO requests.",
  "4G X2 HO success rate": "X2 HO successes / requests.",
  "4G S1 HO successes": "Sum of S1 HO successes.",
  "4G S1 HO requests": "Sum of S1 HO requests.",
  "4G S1 HO success rate": "S1 HO successes / requests.",
  "4G intra-eNB HO requests": "Sum of intra-eNodeB HO requests.",
  "4G intra-eNB HO successes": "Sum of intra-eNodeB HO successes.",
  "4G intra-eNB HO success rate": "Intra-eNB HO successes / requests.",
  "4G intra-system HO success rate": "(X2 successes + S1 successes + intra-eNB successes) / (X2 + S1 + intra-eNB requests).",
  "4G UL user rate (Mbps)": "(PDCP UL user traffic bytes − UL burst tail bytes) / (PDCP UL user data time − UL burst tail time).",
  "4G DL user rate (Mbps)": "(PDCP DL user traffic bytes − DL burst tail bytes) / (PDCP DL user data time − DL burst tail time).",
  "4G CQI < 7 reports": "Count of CQI reports < 7.",
  "4G CQI ≥ 7 reports": "Count of CQI reports ≥ 7.",
  "4G CQI good ratio (≥7)": "CQI ≥ 7 reports / total CQI reports.",
  "4G per-cell daily avg total (GB)": "PDCP UL+DL / total cells.",
  "5G total traffic (TB)": "Sum of RLC UL+DL during the period.",
  "5G total traffic (TB) – CT": "RLC UL+DL for CT users.",
  "5G total traffic (TB) – CU": "RLC UL+DL for CU users.",
  "5G UL PRBs (total occupied)": "Sum of occupied UL PRBs during the period.",
  "5G UL PRBs (total available)": "Sum of available UL PRBs during the period.",
  "5G UL PRB avg utilization": "Occupied UL PRBs / available UL PRBs.",
  "5G DL PRBs (total occupied)": "Sum of occupied DL PRBs during the period.",
  "5G DL PRBs (total available)": "Sum of available DL PRBs during the period.",
  "5G DL PRB avg utilization": "Occupied DL PRBs / available DL PRBs.",
  "5G RRC setup successes": "Sum of RRC setup successes.",
  "5G RRC setup requests": "Sum of RRC setup requests.",
  "5G NG signaling setup successes": "Sum of NG signaling connection setup successes.",
  "5G NG signaling setup requests": "Sum of NG signaling connection setup requests.",
  "5G initial QoSFlow successes": "Sum of initial QoSFlow setup successes.",
  "5G initial QoSFlow requests": "Sum of initial QoSFlow setup requests.",
  "5G radio access success rate": "(RRC success/req) × (NG signaling success/req) × (QoSFlow success/req).",
  "5G CQITable CQI ≥10": "Sum of UE CQI≥10 in 4-bit CQI Table.",
  "5G CQITable2 CQI ≥7": "Sum of UE CQI≥7 in 4-bit CQI Table 2.",
  "5G CQITable total CQI reports": "Sum of UE CQI reports in 4-bit CQI Table.",
  "5G CQITable2 total CQI reports": "Sum of UE CQI reports in 4-bit CQI Table 2.",
  "5G CQI good rate": "(CQI≥10 in Table + CQI≥7 in Table2) / (total in Table + total in Table2).",
  "5G intra-gNB HO requests": "Sum of intra-gNB HO requests.",
  "5G intra-gNB HO successes": "Sum of intra-gNB HO successes.",
  "5G NG inter-site HO requests": "Sum of NG inter-site HO requests.",
  "5G NG inter-site HO successes": "Sum of NG inter-site HO successes.",
  "5G Xn inter-site HO requests": "Sum of Xn inter-site HO requests.",
  "5G Xn inter-site HO successes": "Sum of Xn inter-site HO successes.",
  "5G intra-system HO success rate": "(intra-gNB successes + NG inter-site successes + Xn inter-site successes) / (respective requests).",
  "5G QoSFlow releases (total)": "Total QoSFlow releases.",
  "5G QoSFlow normal releases": "Normal QoSFlow releases.",
  "5G QoSFlow drop rate": "(total − normal) / total.",
  "5G user UL avg throughput": "(RLC UL user traffic − UL tail bytes) / RLC UL user data time (excl. last slot).",
  "5G user DL avg throughput": "(RLC DL user traffic − DL tail bytes) / RLC DL user data time (excl. last slot).",
  "5G per-cell daily avg total (GB)": "RLC UL+DL / total cells.",
  "5G avg RRC connected users": "Sum of avg RRC connected users.",
  "5G daily avg total traffic (TB)": "Average RLC UL+DL during the period.",
  "5G daily avg total traffic (TB) – CT": "Average RLC UL+DL for CT users.",
  "5G daily avg total traffic (TB) – CU": "Average RLC UL+DL for CU users."
}

# --- Group outline (EN) ------------------------------------------------------
group_company_outline = [
    {
        "id": 1, "parentID": None, "title": "Network Scale Assessment", "level": "1",
        "principle": "Rank all 31 provinces by 4G/5G base-station totals and sharing ratio; show structural differences across provinces.",
        "info_needed": [
            {"Number of gNBs": "gnbNums"},
            {"Shared site-sets": "shareSetGnbNums"},
            {"Share of site-sets": "shareSetGnbRate"}
        ],
        "methods": "ranking"
    },
    {
        "id": 2, "parentID": 1, "title": "Sharing Structure Comparison", "level": "2",
        "principle": "Analyze CT/CU sharing asymmetry and progress of dual-mode deployments by province.",
        "info_needed": [
            {"Number of shared cells": "Number of shared cells"},
            {"Total cells – SA": "Total cells – SA"},
            {"Equipment count – dual-mode": "Equipment count – dual-mode"}
        ],
        "methods": "ranking"
    },
    {
        "id": 3, "parentID": None, "title": "Spectrum Efficiency Panorama", "level": "1",
        "principle": "Rank provinces by PRB utilization efficiency and coverage quality.",
        "info_needed": [
            {"5G DL PRB avg utilization": "prbUseddlRate"},
            {"RSRP ≥ −110 share": "RSRP ≥ −110 share"},
            {"5G CQI good rate": "cqiGoodRatio"}
        ],
        "methods": "ranking"
    },
    {
        "id": 4, "parentID": 3, "title": "Coverage Quality Analysis", "level": "2",
        "principle": "Show ranking of MR coverage vs radio-access success correlation by province.",
        "info_needed": [
            {"RSRP ≥ −110 share": "RSRP ≥ −110 share"},
            {"5G radio access success rate": "5G radio access success rate"}
        ],
        "methods": "ranking"
    },
    {
        "id": 5, "parentID": None, "title": "Service Carrying Capacity", "level": "1",
        "principle": "Compare provincial 4/5G traffic scale and network-evolution maturity.",
        "info_needed": [
            {"4/5G total traffic": "4/5G total traffic (B-domain)"},
            {"5G offload ratio (B-domain)": "5G offload ratio (B-domain)"},
            {"5G terminal attach rate (B-domain)": "5G terminal attach rate (B-domain)"}
        ],
        "methods": "ranking"
    },
    {
        "id": 6, "parentID": 5, "title": "Capacity Dynamic Distribution", "level": "2",
        "principle": "Rank high-load provinces by PRB thresholds and offload efficiency.",
        "info_needed": [
            {"4G DL avg PRB utilization": "4G DL avg PRB utilization (%)"},
            {"5G user DL avg throughput": "5G user DL avg throughput"}
        ],
        "methods": "ranking"
    },
    {
        "id": 7, "parentID": None, "title": "Investment Effectiveness", "level": "1",
        "principle": "Assess frequency-clearing progress and equipment reuse benefits by province.",
        "info_needed": [
            {"PRRU count": "PRRU count"},
            {"Equipment count – 2CC&3CC (≥200M)": "Equipment count – 2CC&3CC (≥200M)"},
            {"5G traffic residence ratio (B-domain)": "5G traffic residence ratio (B-domain)"}
        ],
        "methods": "ranking"
    }
]
