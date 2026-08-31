# Red Dead Redemption 2 — Chapter 4: Saint Denis

**Game:** Red Dead Redemption 2  
**Tier:** 1  
**Chapter:** Chapter 4  
**Location:** Saint Denis / Shady Belle  
**Mission Type:** Main Story / Chapter Progression

## Chapter Overview

After events in Rhodes and the kidnapping of Jack Marston, the gang moves toward Saint Denis and operates from Shady Belle.

The source data contains a direct mission reference followed by a source-listed OR relationship containing three alternative mission references. The mission names are normalized into unique mission records while the original source relationship is preserved separately.

## Mission Records

### 1. The Joys of Civilization

**Type:** Main Story Mission  
**Chapter:** 4  
**Location:** Saint Denis  
**Order:** Availability Group 1  
**Branch:** None

Arthur becomes involved in activities and investigations in Saint Denis.

---

### 2. No, No and Thrice, No

**Type:** Main Story Mission  
**Chapter:** 4  
**Location:** Saint Denis / surrounding area  
**Order:** Availability Group 2  
**Branch:** Source-listed OR relationship

Arthur becomes involved in a mission concerning the gang's activities in Saint Denis.

**Source relationship:** Listed as OR with Angelo Bronte, A Man of Honor and Help a Brother Out.

---

### 3. Angelo Bronte, A Man of Honor

**Type:** Main Story Mission  
**Chapter:** 4  
**Location:** Saint Denis  
**Order:** Availability Group 2  
**Branch:** Source-listed OR relationship

Arthur becomes involved with Angelo Bronte and the gang's activities in Saint Denis.

**Source relationship:** Listed as OR with No, No and Thrice, No and Help a Brother Out.

---

### 4. Help a Brother Out

**Type:** Main Story Mission  
**Chapter:** 4  
**Location:** Saint Denis  
**Order:** Availability Group 2  
**Branch:** Source-listed OR relationship

Arthur becomes involved in an encounter connected to activities in Saint Denis.

**Source relationship:** Listed as OR with No, No and Thrice, No and Angelo Bronte, A Man of Honor.

## Mission Availability Structure

The original source contains two mission groups.

### Availability Group 1

The Joys of Civilization

### Availability Group 2

No, No and Thrice, No
        |
        OR
        |
        +---- Angelo Bronte, A Man of Honor
        |
        OR
        |
        +---- Help a Brother Out

## Normalization Rules Applied

- Each unique mission name is stored as one mission record.
- The original mission grouping is preserved.
- The source-listed three-way OR relationship is preserved.
- No additional missions are invented.
- No source mission reference is silently removed.
- Source relationships are preserved without adding unsupported gameplay interpretations.

## Mission Summary

**Unique Mission Records:** 4  
**Availability Groups:** 2  
**Source-listed OR expressions:** 1  
**Repeated Missions Normalized:** No

## Branch Structure

Chapter 4 contains two source-defined mission groups and one source-listed OR relationship.

**OR relationship 1:** No, No and Thrice, No OR Angelo Bronte, A Man of Honor OR Help a Brother Out

## Data Classification

**Tier:** 1  
**Dataset Role:** Main Story Reference  
**Structure Status:** Normalized  
**Availability Status:** Grouped  
**Branch Status:** Source relationships preserved  
**Unique Mission Count:** 4

## Mission Links

1. [[missions/Chapter_4_Saint_Denis/Angelo_Bronte_A_Man_of_Honor|Angelo Bronte, A Man of Honor]]
2. [[missions/Chapter_4_Saint_Denis/Help_a_Brother_Out|Help a Brother Out]]
3. [[missions/Chapter_4_Saint_Denis/No_No_and_Thrice_No|No, No and Thrice, No]]
4. [[missions/Chapter_4_Saint_Denis/The_Joys_of_Civilization|The Joys of Civilization]]

