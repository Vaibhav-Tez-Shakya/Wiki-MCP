# Red Dead Redemption 2 — Chapter 6: Beaver Hollow

**Game:** Red Dead Redemption 2  
**Tier:** 1  
**Chapter:** Chapter 6  
**Location:** Beaver Hollow  
**Mission Type:** Main Story / Chapter Progression

## Chapter Overview

The remaining gang members move north to Beaver Hollow while facing increasing pressure from the Pinkertons and internal conflict.

The source data contains two named mission branches. Each branch contains a direct mission followed by a source-listed three-way OR relationship. Mission names are normalized into unique mission records while the original branch and relationship structures are preserved.

## Mission Records

### 1. That's Murfree Country

**Type:** Main Story Mission  
**Chapter:** 6  
**Location:** Beaver Hollow / surrounding area  
**Order:** Availability Group 1  
**Branch:** That's Murfree Country Branch

Arthur and the gang become involved in activities connected to the Murfree Brood.

---

### 2. The Course of True Love IV

**Type:** Main Story Mission  
**Chapter:** 6  
**Classification Note:** Playable during Chapter 5; treated as a Chapter 6 mission when replaying missions.  
**Location:** Beaver Hollow / surrounding area  
**Order:** Availability Group 1  
**Branch:** That's Murfree Country Branch / Source-listed OR relationship

Arthur becomes involved in the fourth part of The Course of True Love sequence.

**Source relationship:** Listed as OR with Money Lending & Other Sins VI and Visiting Hours.

---

### 3. Money Lending & Other Sins VI

**Type:** Main Story Mission  
**Chapter:** 6  
**Classification Note:** Playable during Chapter 5; treated as a Chapter 6 mission when replaying missions.  
**Location:** Beaver Hollow / surrounding area  
**Order:** Availability Group 1  
**Branch:** That's Murfree Country Branch / Source-listed OR relationship

Arthur undertakes another debt-related task for the gang.

**Source relationship:** Listed as OR with The Course of True Love IV and Visiting Hours.

---

### 4. Visiting Hours

**Type:** Main Story Mission  
**Chapter:** 6  
**Classification Note:** Playable during Chapter 5; treated as a Chapter 6 mission when replaying missions.  
**Location:** Beaver Hollow / surrounding area  
**Order:** Availability Group 1  
**Branch:** That's Murfree Country Branch / Source-listed OR relationship

Arthur becomes involved in an operation connected to an imprisoned gang member.

**Source relationship:** Listed as OR with The Course of True Love IV and Money Lending & Other Sins VI.

---

### 5. A Fork in the Road

**Type:** Main Story Mission  
**Chapter:** 6  
**Location:** Beaver Hollow / surrounding area  
**Order:** Availability Group 2  
**Branch:** A Fork in the Road Branch

Arthur becomes involved in events surrounding his deteriorating situation.

---

### 6. Icarus and Friends

**Type:** Main Story Mission  
**Chapter:** 6  
**Classification Note:** Playable during Chapter 5; treated as a Chapter 6 mission when replaying missions.  
**Location:** Beaver Hollow / surrounding area  
**Order:** Availability Group 2  
**Branch:** A Fork in the Road Branch / Source-listed OR relationship

Arthur participates in an operation involving aerial travel and members of the gang.

**Source relationship:** Listed as OR with Do Not Seek Absolution I and Of Men and Angels I.

---

### 7. Do Not Seek Absolution I

**Type:** Main Story Mission  
**Chapter:** 6  
**Classification Note:** Playable during Chapter 5; treated as a Chapter 6 mission when replaying missions.  
**Location:** Beaver Hollow / surrounding area  
**Order:** Availability Group 2  
**Branch:** A Fork in the Road Branch / Source-listed OR relationship

Arthur becomes involved in the first part of the Do Not Seek Absolution sequence.

**Source relationship:** Listed as OR with Icarus and Friends and Of Men and Angels I.

---

### 8. Of Men and Angels I

**Type:** Main Story Mission  
**Chapter:** 6  
**Classification Note:** Playable during Chapter 5; treated as a Chapter 6 mission when replaying missions.  
**Location:** Beaver Hollow / surrounding area  
**Order:** Availability Group 2  
**Branch:** A Fork in the Road Branch / Source-listed OR relationship

Arthur becomes involved in the first part of the Of Men and Angels sequence.

**Source relationship:** Listed as OR with Icarus and Friends and Do Not Seek Absolution I.

## Mission Availability Structure

The original source contains two named mission branches.

### Availability Group 1 — That's Murfree Country Branch

That's Murfree Country
        |
        +---- The Course of True Love IV
        |
        OR
        |
        +---- Money Lending & Other Sins VI
        |
        OR
        |
        +---- Visiting Hours

### Availability Group 2 — A Fork in the Road Branch

A Fork in the Road
        |
        +---- Icarus and Friends
        |
        OR
        |
        +---- Do Not Seek Absolution I
        |
        OR
        |
        +---- Of Men and Angels I

## Source Relationship Structure

The original source contains two three-way OR relationship expressions.

**OR relationship 1:** The Course of True Love IV OR Money Lending & Other Sins VI OR Visiting Hours

**OR relationship 2:** Icarus and Friends OR Do Not Seek Absolution I OR Of Men and Angels I

The source-listed OR expressions are preserved without adding unsupported gameplay interpretations.

## Normalization Rules Applied

- Each unique mission name is stored as one mission record.
- The two original named branches are preserved.
- Original mission ordering within each branch is preserved.
- Source-listed three-way OR relationships are preserved.
- Each mission participating in a source-listed OR relationship retains a source relationship field.
- No additional missions are invented.
- No source mission reference is silently removed.
- Exact mission spelling and punctuation are preserved, including the '&' in Money Lending & Other Sins VI.
- Source relationships are preserved without adding unsupported gameplay interpretations.

## Mission Summary

**Unique Mission Records:** 8  
**Availability Groups:** 2  
**Source-listed OR expressions:** 2  
**Source relationship fields:** 6  
**Repeated Missions Normalized:** No

## Branch Structure

Chapter 6 contains two source-defined mission branches.

**Branch 1:** That's Murfree Country Branch

**OR relationship 1:** The Course of True Love IV OR Money Lending & Other Sins VI OR Visiting Hours

**Branch 2:** A Fork in the Road Branch

**OR relationship 2:** Icarus and Friends OR Do Not Seek Absolution I OR Of Men and Angels I

## Data Classification

**Tier:** 1  
**Dataset Role:** Main Story Reference  
**Structure Status:** Normalized  
**Availability Status:** Grouped  
**Branch Status:** Source branches and relationships preserved  
**Unique Mission Count:** 8

## Mission Links

1. [[missions/Chapter_6_Beaver_Hollow/A_Fork_in_the_Road|A Fork in the Road]]
2. [[missions/Chapter_6_Beaver_Hollow/Do_Not_Seek_Absolution_I|Do Not Seek Absolution I]]
3. [[missions/Chapter_6_Beaver_Hollow/Icarus_and_Friends|Icarus and Friends]]
4. [[missions/Chapter_6_Beaver_Hollow/Money_Lending_Other_Sins_VI|Money Lending & Other Sins VI]]
5. [[missions/Chapter_6_Beaver_Hollow/Of_Men_and_Angels_I|Of Men and Angels I]]
6. [[missions/Chapter_6_Beaver_Hollow/The_Course_of_True_Love_IV|The Course of True Love IV]]
7. [[missions/Chapter_6_Beaver_Hollow/Visiting_Hours|Visiting Hours]]

