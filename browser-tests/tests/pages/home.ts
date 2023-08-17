import { screen } from '@testing-library/testcafe';
import { envUrl } from '../utils/settings';

export const route = () => `${envUrl()}/admin`;
