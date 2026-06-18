import { Router, type IRouter } from "express";
import healthRouter from "./health";
import searchRouter from "./search";
import productsRouter from "./products";
import categoriesRouter from "./categories";
import brandsRouter from "./brands";
import trendingRouter from "./trending";

const router: IRouter = Router();

router.use(healthRouter);
router.use(searchRouter);
router.use(productsRouter);
router.use(categoriesRouter);
router.use(brandsRouter);
router.use(trendingRouter);

export default router;
