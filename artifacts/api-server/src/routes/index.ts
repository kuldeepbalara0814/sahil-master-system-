import { Router, type IRouter } from "express";
import healthRouter from "./health";
import sahilRouter from "./sahil";

const router: IRouter = Router();

router.use(healthRouter);
router.use("/sahil", sahilRouter);

export default router;
