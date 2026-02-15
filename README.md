# RISEMASTER Backend

**RISEMASTER** is an AI-powered adaptive learning platform designed to help Rwandan secondary school students (S1–S6) improve their mathematics performance using real REB national examination past papers. The platform emphasizes **individual educational gain** through Bayesian Knowledge Tracing (BKT), scaffolded step-by-step guidance, multi-level hints, and teen-friendly concept introductions.

This repository contains the **backend API** — a lightweight Flask application that powers the core intelligent features of the platform.

## Project Overview

**Full Title**  
Modeling Individual Educational Gain in STEM: An AI-Powered Platform for Tracking and Rewarding Learning Progress in African Higher Education

## Current Progress

The backend is a functional MVP with the following completed features:

- User registration with class level (S1–S6) to determine appropriate REB past-paper level (S3 or S6)
- Adaptive problem selection based on weakest skill (using BKT mastery probability)
- Scaffolded learning: full REB-style questions broken into ordered sub-steps
- Multi-level hints per step
- Teen-friendly, conversational concept introductions before each problem
- Logging of every student interaction (correctness, hints used, time taken)
- Real-time mastery probability updates using **pyBKT** (Bayesian Knowledge Tracing)
- Interactive Swagger documentation
- SQLite database for development

### Implemented Endpoints


| Method | Endpoint                        | Description                                                                                     | Status    |
|--------|---------------------------------|-------------------------------------------------------------------------------------------------|-----------|
| POST   | `/users/register`               | Register a new student (name, email, class_level)                                               | Complete  |
| POST   | `/problems/next`                | Get next adaptive problem + teen-friendly concept intro + scaffolded steps + hints             | Complete  |
| POST   | `/interactions/submit`          | Submit answer to a step → log interaction → update BKT mastery probability                      | Complete  |

**Planned / future endpoints**:
- GET `/users/:id/progress` (mastery & gain data for dashboard)
- GET `/topics` (list available topics)
- Authentication (JWT)
