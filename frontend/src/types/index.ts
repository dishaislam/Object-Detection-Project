/**
 * TypeScript type definitions for the application
 */

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface SignupData {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  class_name: string;
  confidence: number;
  bounding_box: BoundingBox;
}

export interface DetectionResponse {
  annotated_image: string;
  detections: Detection[];
  processing_time: number;
}

export interface QuestionRequest {
  question: string;
  detections: Detection[];
  image_base64?: string;
}

export interface AnswerResponse {
  answer: string;
  processing_time: number;
}