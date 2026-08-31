# Red Dead Redemption 2 — Chapter 2: Horseshoe Overlook

**Game:** Red Dead Redemption 2  
**Tier:** 1  
**Chapter:** Chapter 2  
**Location:** Horseshoe Overlook  
**Mission Type:** Main Story / Chapter Progression

## Chapter Overview

Chapter 2 begins after the Van der Linde gang leaves the mountains and establishes camp at Horseshoe Overlook near Valentine.

The source data contains multiple mission groups with overlapping references. Repeated mission references are normalized into unique mission records, while the original group structure and source-listed OR relationships are preserved separately.

## Mission Records

### 1. Who is Not Without Sin

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Horseshoe Overlook / Valentine  
**Order:** Availability Group 1  
**Branch:** None

Arthur becomes involved in Reverend Swanson's situation.

---

### 2. A Strange Kindness

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Horseshoe Overlook  
**Order:** Availability Groups 1 and 2  
**Branch:** None

The gang investigates a possible new camp location.

**Source references:** Appears in multiple mission groups. Normalized as one unique mission record.

---

### 3. Exit Pursued by a Bruised Ego

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Horseshoe Overlook / Valentine area  
**Order:** Availability Group 2  
**Branch:** None

Arthur assists Hosea with a hunting and horse-related expedition.

---

### 4. The Spines of America

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Valentine / surrounding area  
**Order:** Availability Group 2  
**Branch:** None

Arthur assists Hosea with a robbery involving a homestead.

---

### 5. The Sheep and the Goats

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Valentine  
**Order:** Availability Groups 2 and 3  
**Branch:** None

Arthur and John become involved in the handling and movement of sheep.

**Source references:** Appears in multiple mission groups. Normalized as one unique mission record.

---

### 6. Polite Society, Valentine Style

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Valentine  
**Order:** Availability Group 3  
**Branch:** None

Arthur and other members of the gang interact with people and activities around Valentine.

---

### 7. Good, Honest, Snake Oil

**Type:** Stranger / Side Mission  
**Chapter:** 2  
**Location:** Valentine  
**Order:** Availability Group 3  
**Branch:** None

Arthur becomes involved in a bounty-related encounter involving a fraudulent medicine seller.

---

### 8. Pouring Forth Oil I

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Valentine / surrounding area  
**Order:** Availability Group 3  
**Branch:** Pouring Forth Oil sequence

The first part of the Pouring Forth Oil sequence begins.

---

### 9. Pouring Forth Oil II

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Valentine / surrounding area  
**Order:** Availability Group 3  
**Branch:** Pouring Forth Oil sequence

The second part of the Pouring Forth Oil sequence continues preparations for the planned train robbery.

---

### 10. Pouring Forth Oil III

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Valentine / surrounding area  
**Order:** Availability Group 3  
**Branch:** Pouring Forth Oil sequence

The third part of the sequence advances preparations for the train robbery.

---

### 11. Pouring Forth Oil IV

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Valentine / surrounding area  
**Order:** Availability Group 3  
**Branch:** Source-listed OR relationship

The fourth part of the Pouring Forth Oil sequence.

**Source relationship:** Listed as OR with A Fisher of Men.

---

### 12. A Fisher of Men

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Valentine / surrounding area  
**Order:** Availability Group 3  
**Branch:** Source-listed OR relationship

Arthur spends time with Jack Marston during a fishing trip.

**Source relationship:** Listed as OR with Pouring Forth Oil IV.

---

### 13. Americans at Rest

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Valentine  
**Order:** Availability Group 4  
**Branch:** None

Arthur becomes involved in a confrontation at the saloon in Valentine.

---

### 14. The First Shall Be Last

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Valentine / surrounding area  
**Order:** Availability Group 4  
**Branch:** Source-listed OR relationship

Arthur participates in an effort to rescue a gang member.

**Source relationship:** Listed as OR with Paying a Social Call and Money Lending and Other Sins I.

---

### 15. Paying a Social Call

**Type:** Main Story Mission  
**Chapter:** 2  
**Location:** Six Point Cabin / surrounding area  
**Order:** Availability Group 4  
**Branch:** Source-listed OR relationship

Arthur and members of the gang visit an O'Driscoll hideout.

**Source relationship:** Listed as OR with The First Shall Be Last and Money Lending and Other Sins I.

---

### 16. Money Lending and Other Sins I

**Type:** Stranger / Camp Mission  
**Chapter:** 2  
**Location:** Horseshoe Overlook  
**Order:** Availability Group 4  
**Branch:** Source-listed OR relationship

Arthur undertakes a debt-collection task for Leopold Strauss.

**Source relationship:** Listed as OR with The First Shall Be Last and Paying a Social Call.

## Mission Availability Structure

The original source contains four mission groups.

### Availability Group 1

Who is Not Without Sin
        +
A Strange Kindness

### Availability Group 2

Exit Pursued by a Bruised Ego
        +
The Spines of America
        +
The Sheep and the Goats
        +
A Strange Kindness

### Availability Group 3

Polite Society, Valentine Style
        +
Good, Honest, Snake Oil
        +
Pouring Forth Oil I
        +
Pouring Forth Oil II
        +
Pouring Forth Oil III
        |
        +---- Pouring Forth Oil IV
        |
        OR
        |
        +---- A Fisher of Men
        +
The Sheep and the Goats
        +
A Strange Kindness

### Availability Group 4

Americans at Rest
        |
        +---- The First Shall Be Last
        |
        OR
        +---- Paying a Social Call
        |
        OR
        +---- Money Lending and Other Sins I

## Normalization Rules Applied

- Repeated mission names are stored as one unique mission record.
- Mission availability groups are preserved.
- Source-listed OR relationships are preserved.
- Pouring Forth Oil I–IV remains a sequence.
- No additional missions are invented.
- No source mission reference is silently removed.
- Source relationships are preserved without adding unsupported gameplay interpretations.

## Mission Summary

**Unique Mission Records:** 16  
**Availability Groups:** 4  
**Source-listed OR expressions:** 2  
**Repeated Missions Normalized:** Yes

## Branch Structure

Chapter 2 contains overlapping availability groups and source-listed OR relationships.

**OR relationship 1:** Pouring Forth Oil IV OR A Fisher of Men

**OR relationship 2:** The First Shall Be Last OR Paying a Social Call OR Money Lending and Other Sins I

## Data Classification

**Tier:** 1  
**Dataset Role:** Main Story Reference  
**Structure Status:** Normalized  
**Availability Status:** Grouped  
**Branch Status:** Source relationships preserved  
**Unique Mission Count:** 16

## Mission Links

1. [[missions/Chapter_2_Horseshoe_Overlook/A_Fisher_of_Men|A Fisher of Men]]
2. [[missions/Chapter_2_Horseshoe_Overlook/A_Strange_Kindness|A Strange Kindness]]
3. [[missions/Chapter_2_Horseshoe_Overlook/Americans_at_Rest|Americans at Rest]]
4. [[missions/Chapter_2_Horseshoe_Overlook/Exit_Pursued_by_a_Bruised_Ego|Exit Pursued by a Bruised Ego]]
5. [[missions/Chapter_2_Horseshoe_Overlook/Good_Honest_Snake_Oil|Good, Honest, Snake Oil]]
6. [[missions/Chapter_2_Horseshoe_Overlook/Money_Lending_and_Other_Sins_I|Money Lending and Other Sins I]]
7. [[missions/Chapter_2_Horseshoe_Overlook/Paying_a_Social_Call|Paying a Social Call]]
8. [[missions/Chapter_2_Horseshoe_Overlook/Polite_Society_Valentine_Style|Polite Society, Valentine Style]]
9. [[missions/Chapter_2_Horseshoe_Overlook/Pouring_Forth_Oil_I|Pouring Forth Oil I]]
10. [[missions/Chapter_2_Horseshoe_Overlook/Pouring_Forth_Oil_II|Pouring Forth Oil II]]
11. [[missions/Chapter_2_Horseshoe_Overlook/Pouring_Forth_Oil_III|Pouring Forth Oil III]]
12. [[missions/Chapter_2_Horseshoe_Overlook/Pouring_Forth_Oil_IV|Pouring Forth Oil IV]]
13. [[missions/Chapter_2_Horseshoe_Overlook/The_First_Shall_Be_Last|The First Shall Be Last]]
14. [[missions/Chapter_2_Horseshoe_Overlook/The_Sheep_and_the_Goats|The Sheep and the Goats]]
15. [[missions/Chapter_2_Horseshoe_Overlook/The_Spines_of_America|The Spines of America]]
16. [[missions/Chapter_2_Horseshoe_Overlook/Who_is_Not_Without_Sin|Who is Not Without Sin]]

